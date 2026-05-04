import re
import io
import pytesseract
import PyPDF2

from .image_handler import optimize_for_ocr
from .schemas import Ingredient, Recipe
from .weight_converter import to_grams


UNITS = [
    "tablespoons", "tablespoon", "tbsp", "tbs",
    "teaspoons", "teaspoon", "tsp",
    "cups", "cup",
    "ounces", "ounce", "oz",
    "pounds", "pound", "lbs", "lb",
    "grams", "gram",
    "kilograms", "kilogram", "kg",
    "milliliters", "milliliter", "ml",
    "liters", "liter",
    "fluid ounces", "fluid ounce", "fl oz",
    "pints", "pint", "pt",
    "quarts", "quart", "qt",
    "gallons", "gallon",
    "sticks", "stick",
    "packages", "package", "pkg",
    "cans", "can",
    "cloves", "clove",
    "pinches", "pinch",
    "dashes", "dash",
]

UNIT_PATTERN = "|".join(sorted(UNITS, key=len, reverse=True))

SECTION_INGREDIENTS = re.compile(
    r"^(ingredients?|what you need|ingredient list)\s*:?\s*$", re.IGNORECASE
)
SECTION_INSTRUCTIONS = re.compile(
    r"^(instructions?|directions?|method|steps?|preparation|how to (make|prepare))\s*:?\s*$",
    re.IGNORECASE,
)

QUANTITY_RE = r"[\d\s/½¼¾⅓⅔⅛⅜⅝⅞.]+"
INGREDIENT_RE = re.compile(
    rf"^({QUANTITY_RE})?\s*({UNIT_PATTERN})\.?\s+(.+?)(?:,\s*(.+))?$",
    re.IGNORECASE,
)


def extract_text_from_image(image_bytes: bytes) -> str:
    import logging
    logger = logging.getLogger(__name__)
    try:
        logger.info("Optimizing image for OCR...")
        img = optimize_for_ocr(image_bytes)
        logger.info(f"Image optimized: {img.size}")
        logger.info("Running Tesseract OCR...")
        # PSM 3 = fully automatic page segmentation (handles columns/mixed layouts)
        # OEM 1 = LSTM engine only (most accurate)
        text = pytesseract.image_to_string(img, lang="eng", config="--psm 3 --oem 1")
        logger.info(f"OCR returned {len(text)} characters")
        return text
    except Exception as e:
        logger.error(f"OCR failed: {e}", exc_info=True)
        raise


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def _parse_ingredient_line(line: str, index: int) -> Ingredient | None:
    line = line.strip()
    if not line:
        return None

    m = INGREDIENT_RE.match(line)
    if m:
        qty, unit, name, prep = m.groups()
        qty = qty.strip() if qty else None
        unit = unit.strip().lower() if unit else None
        name = name.strip()
        grams = to_grams(qty, unit, name)
        return Ingredient(
            raw=line,
            quantity=qty,
            unit=unit,
            name=name,
            prep=prep.strip() if prep else None,
            grams=grams,
            color_index=index,
        )

    # Line starts with a number but didn't match a unit — likely "2 eggs" or "3 large apples"
    m2 = re.match(rf"^({QUANTITY_RE})\s+(large|medium|small|whole)?\s*(.+?)(?:,\s*(.+))?$", line, re.IGNORECASE)
    if m2:
        qty, size, name, prep = m2.groups()
        name = (f"{size} {name}".strip() if size else name).strip()
        return Ingredient(
            raw=line,
            quantity=qty.strip() if qty else None,
            unit=None,
            name=name,
            prep=prep.strip() if prep else None,
            grams=None,
            color_index=index,
        )

    # Fallback: treat whole line as ingredient name
    return Ingredient(raw=line, name=line, color_index=index)


def _parse_steps(lines: list[str]) -> list[str]:
    steps, current = [], []
    for line in lines:
        if re.match(r"^\d+[\.\):]?\s", line):
            if current:
                steps.append(" ".join(current))
                current = []
            current.append(re.sub(r"^\d+[\.\):]?\s+", "", line).strip())
        elif line:
            current.append(line)
    if current:
        steps.append(" ".join(current))
    return steps


def _extract_metadata(lines: list[str]) -> dict:
    meta = {}
    for line in lines:
        low = line.lower()
        if "servings" in low or "serves" in low or "yield" in low:
            m = re.search(r"(\d+)", line)
            if m:
                meta["servings"] = m.group(1)
        if "prep" in low and "time" in low:
            m = re.search(r"(\d+\s*(?:hr|hour|min|minute)s?(?:\s+\d+\s*(?:min|minute)s?)?)", line, re.IGNORECASE)
            if m:
                meta["prep_time"] = m.group(1)
        if "cook" in low and "time" in low:
            m = re.search(r"(\d+\s*(?:hr|hour|min|minute)s?(?:\s+\d+\s*(?:min|minute)s?)?)", line, re.IGNORECASE)
            if m:
                meta["cook_time"] = m.group(1)
    return meta


def parse_recipe(text: str) -> Recipe:
    lines = [l.strip() for l in text.splitlines()]
    lines = [l for l in lines if l]

    if not lines:
        return Recipe(title="Untitled Recipe")

    title = lines[0]

    ing_start = inst_start = -1
    for i, line in enumerate(lines):
        if SECTION_INGREDIENTS.match(line):
            ing_start = i + 1
        elif SECTION_INSTRUCTIONS.match(line):
            inst_start = i + 1

    if ing_start != -1 and inst_start != -1:
        ingredient_lines = lines[ing_start : inst_start - 1]
        step_lines = lines[inst_start:]
    elif ing_start != -1:
        ingredient_lines = lines[ing_start:]
        step_lines = []
    else:
        # Heuristic split: lines starting with digits/fractions → ingredients
        ingredient_lines, step_lines = [], []
        for line in lines[1:]:
            if re.match(r"^[\d¼½¾⅓⅔⅛]", line):
                ingredient_lines.append(line)
            else:
                step_lines.append(line)

    ingredients = [
        ing
        for i, line in enumerate(ingredient_lines)
        if (ing := _parse_ingredient_line(line, i)) is not None
    ]

    steps = _parse_steps(step_lines)
    meta = _extract_metadata(lines[:10])

    return Recipe(
        title=title,
        ingredients=ingredients,
        steps=steps,
        **meta,
    )
