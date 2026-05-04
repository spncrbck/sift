import json
import re
from pathlib import Path

_chart: dict = {}


def _load():
    global _chart
    if not _chart:
        path = Path(__file__).parent.parent / "data" / "weight_chart.json"
        with open(path) as f:
            _chart = json.load(f)


UNICODE_FRACTIONS = {
    "½": 0.5, "¼": 0.25, "¾": 0.75,
    "⅓": 1/3, "⅔": 2/3,
    "⅛": 0.125, "⅜": 0.375, "⅝": 0.625, "⅞": 0.875,
}

UNIT_ALIASES = {
    "cup": "cup", "cups": "cup", "c": "cup",
    "tablespoon": "tablespoon", "tablespoons": "tablespoon",
    "tbsp": "tablespoon", "tbs": "tablespoon", "tb": "tablespoon",
    "teaspoon": "teaspoon", "teaspoons": "teaspoon",
    "tsp": "teaspoon", "t": "teaspoon",
}


def parse_quantity(qty_str: str) -> float | None:
    if not qty_str:
        return None
    s = qty_str.strip()
    for char, val in UNICODE_FRACTIONS.items():
        s = s.replace(char, f" {val}")
    s = s.strip()
    mixed = re.match(r"^(\d+)\s+(\d+)/(\d+)$", s)
    if mixed:
        w, n, d = map(int, mixed.groups())
        return w + n / d
    frac = re.match(r"^(\d+)/(\d+)$", s)
    if frac:
        n, d = map(int, frac.groups())
        return n / d
    try:
        return float(s)
    except ValueError:
        return None


def _lookup(name: str) -> dict | None:
    _load()
    key = name.lower().strip()
    if key in _chart:
        return _chart[key]
    for chart_key in _chart:
        if chart_key in key or key in chart_key:
            return _chart[chart_key]
    return None


def to_grams(quantity: str | None, unit: str | None, ingredient_name: str) -> float | None:
    if not unit or not quantity:
        return None
    canonical = UNIT_ALIASES.get(unit.lower().strip())
    if not canonical:
        return None
    qty = parse_quantity(quantity)
    if qty is None:
        return None
    entry = _lookup(ingredient_name)
    if not entry or canonical not in entry:
        return None
    return round(qty * entry[canonical], 1)
