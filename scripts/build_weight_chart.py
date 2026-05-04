#!/usr/bin/env python3
"""Convert data/king_arthur.csv → data/weight_chart.json.

Each row's teaspoon/tablespoon/cup columns record the *count of that unit*
that equals the gram weight in the grams column. For example:
  All-Purpose Flour: 48 tsp = 16 tbsp = 1 cup = 120g
  Baking powder:     1 tsp  = 1/3 tbsp = 1/48 cup = 4g

Formula:  grams_per_unit = grams / unit_count
"""
import csv
import json
import re
from pathlib import Path

HERE = Path(__file__).parent
CSV_PATH = HERE.parent / "data" / "king_arthur.csv"
OUT_PATH = HERE.parent / "data" / "weight_chart.json"


def parse_fraction(s: str) -> float | None:
    s = s.strip()
    if not s:
        return None
    # Mixed number: "1 2/3"
    m = re.match(r"^(\d+)\s+(\d+)/(\d+)$", s)
    if m:
        w, n, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return w + n / d
    # Simple fraction: "3/4"
    m = re.match(r"^(\d+)/(\d+)$", s)
    if m:
        return int(m.group(1)) / int(m.group(2))
    # Decimal/integer
    try:
        return float(s)
    except ValueError:
        return None


def parse_grams(s: str) -> float | None:
    s = s.strip()
    if not s:
        return None
    # Range: "140 to 170" — take average
    m = re.search(r"([\d./]+(?:\s+\d+/\d+)?)\s+to\s+([\d./]+(?:\s+\d+/\d+)?)", s)
    if m:
        lo = parse_fraction(m.group(1))
        hi = parse_fraction(m.group(2))
        if lo is not None and hi is not None:
            return (lo + hi) / 2
    return parse_fraction(s)


def normalize_name(raw: str) -> str:
    return raw.strip().strip("'").lower()


chart: dict = {}

with open(CSV_PATH, newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        name = normalize_name(row["Ingredient"])
        grams = parse_grams(row["grams"])
        if not grams:
            continue

        entry: dict = {}

        cup = parse_fraction(row["cup"])
        if cup:
            entry["cup"] = round(grams / cup, 1)

        tbsp = parse_fraction(row["tablespoon"])
        if tbsp:
            entry["tablespoon"] = round(grams / tbsp, 1)

        tsp = parse_fraction(row["teaspoon"])
        if tsp:
            entry["teaspoon"] = round(grams / tsp, 1)

        large = parse_fraction(row.get("large", ""))
        if large:
            entry["each"] = round(grams / large, 1)

        if entry and name not in chart:  # first occurrence wins (e.g. yeast packet sizes)
            chart[name] = entry

with open(OUT_PATH, "w") as f:
    json.dump(chart, f, indent=2, ensure_ascii=False)

print(f"✓ {len(chart)} entries written to {OUT_PATH}")
