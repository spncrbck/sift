from pydantic import BaseModel
from typing import Optional


class Ingredient(BaseModel):
    raw: str
    quantity: Optional[str] = None
    unit: Optional[str] = None
    name: str
    prep: Optional[str] = None
    grams: Optional[float] = None
    color_index: int = 0


class Recipe(BaseModel):
    title: str
    source: Optional[str] = None
    servings: Optional[str] = None
    prep_time: Optional[str] = None
    cook_time: Optional[str] = None
    ingredients: list[Ingredient] = []
    steps: list[str] = []
