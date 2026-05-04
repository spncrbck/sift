import re
from .schemas import Recipe

COLORS = [
    {"dot": "#E06C75", "bg": "#FADBD8", "text": "#7B241C"},
    {"dot": "#61AFEF", "bg": "#D6EAF8", "text": "#1A5276"},
    {"dot": "#98C379", "bg": "#D5F5E3", "text": "#1E8449"},
    {"dot": "#E5C07B", "bg": "#FDEBD0", "text": "#7D6608"},
    {"dot": "#C678DD", "bg": "#F4ECF7", "text": "#7D3C98"},
    {"dot": "#56B6C2", "bg": "#D1F2EB", "text": "#148F77"},
    {"dot": "#D19A66", "bg": "#FEF0E0", "text": "#935116"},
    {"dot": "#BE5046", "bg": "#FADBD8", "text": "#7B241C"},
    {"dot": "#528BFF", "bg": "#D6E4FF", "text": "#1A3A80"},
    {"dot": "#41A6B5", "bg": "#D1ECF1", "text": "#0C5460"},
    {"dot": "#B5890F", "bg": "#FEF9C3", "text": "#7D6608"},
    {"dot": "#89DDFF", "bg": "#D0F4FF", "text": "#0A5980"},
]


def _color(index: int) -> dict:
    return COLORS[index % len(COLORS)]


def _fmt_qty(qty: str | None, unit: str | None) -> str:
    parts = []
    if qty:
        parts.append(qty)
    if unit:
        parts.append(unit)
    return " ".join(parts)


def _fmt_grams(grams: float | None) -> str:
    if grams is None:
        return ""
    return f"{int(grams)}g" if grams == int(grams) else f"{grams}g"


def _highlight_ingredients(text: str, recipe: Recipe) -> str:
    # Sort longest-name-first to prevent partial substitutions
    ings = sorted(recipe.ingredients, key=lambda i: len(i.name), reverse=True)
    for ing in ings:
        c = _color(ing.color_index)
        pill = (
            f'<span class="pill" style="background:{c["bg"]};color:{c["text"]}">'
            f"{ing.name}</span>"
        )
        pattern = re.compile(r"\b" + re.escape(ing.name) + r"s?\b", re.IGNORECASE)
        text = pattern.sub(pill, text, count=1)
    return text


def _ingredient_rows(recipe: Recipe) -> str:
    rows = []
    for ing in recipe.ingredients:
        c = _color(ing.color_index)
        qty_display = _fmt_qty(ing.quantity, ing.unit)
        metric = _fmt_grams(ing.grams)
        name_display = ing.name
        if ing.prep:
            name_display += f", <span style='color:#888'>{ing.prep}</span>"
        rows.append(
            f'<div class="ingredient-row">'
            f'<span class="dot" style="background:{c["dot"]}"></span>'
            f'<span class="qty">{qty_display}</span>'
            f'<span class="ing-name">{name_display}</span>'
            f'<span class="metric">{metric}</span>'
            f"</div>"
        )
    return "\n".join(rows)


def _steps_html(recipe: Recipe) -> str:
    items = []
    for i, step in enumerate(recipe.steps, 1):
        highlighted = _highlight_ingredients(step, recipe)
        items.append(
            f'<li class="step">'
            f'<span class="step-num">{i}</span>'
            f'<span class="step-text">{highlighted}</span>'
            f"</li>"
        )
    return "\n".join(items)


def _meta_html(recipe: Recipe) -> str:
    parts = []
    if recipe.source:
        parts.append(f"<span>{recipe.source}</span>")
    if recipe.servings:
        parts.append(f"<span>Serves {recipe.servings}</span>")
    if recipe.prep_time:
        parts.append(f"<span>Prep {recipe.prep_time}</span>")
    if recipe.cook_time:
        parts.append(f"<span>Cook {recipe.cook_time}</span>")
    if not parts:
        return ""
    return f'<div class="meta">{"".join(parts)}</div>'


CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: 'DM Sans', sans-serif;
  font-size: 11pt;
  color: #2c2c2c;
  background: #fff;
  padding: 0.5in;
  max-width: 8.5in;
  margin: 0 auto;
}
h1 {
  font-family: 'Lora', serif;
  font-size: 24pt;
  font-weight: 600;
  line-height: 1.2;
  margin-bottom: 6px;
}
.meta {
  color: #888;
  font-size: 9.5pt;
  margin-bottom: 14px;
  display: flex;
  gap: 0;
  flex-wrap: wrap;
}
.meta span + span::before { content: ' · '; margin: 0 6px; }
hr { border: none; border-top: 1px solid #e8e8e8; margin: 14px 0; }
h2 {
  font-family: 'Lora', serif;
  font-size: 10pt;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: #999;
  margin-bottom: 10px;
}
.ingredients-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 3px 28px;
  margin-bottom: 16px;
}
.ingredient-row {
  display: flex;
  align-items: baseline;
  gap: 7px;
  font-size: 10.5pt;
  padding: 2px 0;
}
.dot {
  width: 8px; height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
  position: relative; top: -1px;
}
.qty {
  min-width: 68px;
  color: #444;
  flex-shrink: 0;
  font-variant-numeric: tabular-nums;
}
.ing-name { flex: 1; }
.metric { color: #bbb; font-size: 9pt; flex-shrink: 0; }
ol.steps { list-style: none; }
.step {
  display: flex;
  gap: 12px;
  margin-bottom: 9px;
  line-height: 1.55;
  font-size: 10.5pt;
}
.step-num {
  font-family: 'Lora', serif;
  font-size: 14pt;
  font-weight: 600;
  color: #ddd;
  flex-shrink: 0;
  min-width: 22px;
  line-height: 1.3;
}
.step-text { flex: 1; }
.pill {
  display: inline;
  padding: 1px 6px;
  border-radius: 10px;
  font-size: 9.5pt;
  font-weight: 500;
}
@media print {
  @page { margin: 0.5in; }
  body { padding: 0; }
}
"""


def render_recipe(recipe: Recipe) -> str:
    title = recipe.title or "Recipe"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Lora:wght@400;600&family=DM+Sans:wght@400;500&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
<h1>{title}</h1>
{_meta_html(recipe)}
<hr>
<h2>Ingredients</h2>
<div class="ingredients-grid">
{_ingredient_rows(recipe)}
</div>
<hr>
<h2>Directions</h2>
<ol class="steps">
{_steps_html(recipe)}
</ol>
</body>
</html>"""
