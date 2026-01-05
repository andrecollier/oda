"""Models for Oda.no recipes and products."""

from pydantic import BaseModel, Field


class RecipeIngredient(BaseModel):
    """Ingredient in a recipe."""

    name: str
    amount: str | None = None
    unit: str | None = None
    product_url: str | None = None  # Link to product on Oda if available


class Recipe(BaseModel):
    """Recipe from Oda.no."""

    id: str
    title: str
    url: str
    image_url: str | None = None
    description: str | None = None
    servings: int = 4
    cooking_time: str | None = None  # e.g., "30 min"
    difficulty: str | None = None  # e.g., "Lett", "Medium"

    ingredients: list[RecipeIngredient] = Field(default_factory=list)
    instructions: list[str] = Field(default_factory=list)

    categories: list[str] = Field(default_factory=list)  # e.g., ["Middag", "Kylling"]
    tags: list[str] = Field(default_factory=list)  # e.g., ["Barnevennlig", "Rask"]

    protein_per_serving: float | None = None
    calories_per_serving: float | None = None

    @property
    def is_family_friendly(self) -> bool:
        """Check if recipe is marked as family/child-friendly."""
        family_keywords = ["barnevennlig", "barn", "familie", "familievennlig"]
        all_text = " ".join(self.tags + self.categories + [self.title]).lower()
        return any(keyword in all_text for keyword in family_keywords)

    @property
    def is_meal_prep_friendly(self) -> bool:
        """Check if recipe is suitable for meal prep."""
        prep_keywords = ["meal prep", "mealprep", "fryser", "oppbevaring", "instant pot"]
        all_text = " ".join(self.tags + self.categories + [self.description or ""]).lower()
        return any(keyword in all_text for keyword in prep_keywords)

    @property
    def is_high_protein(self) -> bool:
        """Check if recipe has high protein content (>25g per serving)."""
        return self.protein_per_serving is not None and self.protein_per_serving >= 25

    @property
    def main_vegetables(self) -> list[str]:
        """Extract main vegetables from ingredients."""
        vegetable_keywords = [
            "brokkoli",
            "gulrot",
            "paprika",
            "løk",
            "tomat",
            "agurk",
            "salat",
            "squash",
            "gresskar",
            "mais",
            "erter",
            "bønner",
            "spinat",
            "grønnkål",
            "blomkål",
            "kålrot",
            "selleri",
        ]

        vegetables = []
        for ingredient in self.ingredients:
            name_lower = ingredient.name.lower()
            for veg in vegetable_keywords:
                if veg in name_lower:
                    vegetables.append(veg)
                    break
        return list(set(vegetables))


class Deal(BaseModel):
    """Oda weekly deal/discount."""

    product_name: str
    product_url: str
    original_price: float
    sale_price: float
    discount_type: str  # "percentage", "2-for-1", "3-for-1", "3-for-2", "fixed"
    discount_value: float  # 30.0 for 30%, 2.0 for 2-for-1
    valid_until: str | None = None
    image_url: str | None = None

    @property
    def savings_amount(self) -> float:
        """Calculate savings amount in kr."""
        return self.original_price - self.sale_price

    @property
    def savings_percentage(self) -> float:
        """Calculate savings percentage."""
        if self.original_price > 0:
            return (self.savings_amount / self.original_price) * 100
        return 0.0


class ProductAlternative(BaseModel):
    """Alternative product option for an ingredient."""

    name: str
    price: float
    unit_price: float | None = None  # kr/kg
    unit_price_text: str | None = None  # "kr 19.90/kg"
    product_url: str
    is_on_deal: bool = False
    deal_info: Deal | None = None

    # Quality indicators
    is_bulk: bool = False  # "pose", "løsvekt"
    is_precut: bool = False  # "kuttet", "ferdig"

    @property
    def savings_percentage(self) -> float:
        """Calculate savings percentage if on deal."""
        if self.deal_info:
            return self.deal_info.savings_percentage
        return 0.0

    @property
    def savings_amount(self) -> float:
        """Calculate savings amount if on deal."""
        if self.deal_info:
            return self.deal_info.savings_amount
        return 0.0
