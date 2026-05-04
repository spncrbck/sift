import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.recipe_parser import parse_recipe

SAMPLE = """Classic Chocolate Chip Cookies

Ingredients
2 1/4 cups all-purpose flour
1 teaspoon baking soda
1 teaspoon salt
1 cup butter, softened
3/4 cup granulated sugar
3/4 cup brown sugar
2 large eggs
2 teaspoons vanilla extract
2 cups chocolate chips

Directions
1. Preheat oven to 375°F.
2. Mix flour, baking soda, and salt in a bowl.
3. Beat butter and sugars until creamy. Add eggs and vanilla extract.
4. Gradually blend in the flour mixture. Stir in chocolate chips.
5. Drop rounded tablespoons onto ungreased baking sheets.
6. Bake 9 to 11 minutes or until golden brown.
"""


def test_parse_title():
    r = parse_recipe(SAMPLE)
    assert r.title == "Classic Chocolate Chip Cookies"


def test_parse_ingredients():
    r = parse_recipe(SAMPLE)
    names = [i.name for i in r.ingredients]
    assert "all-purpose flour" in names
    assert "butter" in names


def test_parse_steps():
    r = parse_recipe(SAMPLE)
    assert len(r.steps) == 6


def test_gram_conversion():
    r = parse_recipe(SAMPLE)
    flour = next(i for i in r.ingredients if i.name == "all-purpose flour")
    assert flour.grams == 270.0  # 2.25 cups * 120g
