"""Pydantic models for Kassal.app API responses."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class Store(BaseModel):
    """Store information."""

    name: str
    code: str
    url: str | None = None
    logo: str | None = None


class NutritionItem(BaseModel):
    """Nutrition information per 100g/ml."""

    code: str
    display_name: str
    amount: float
    unit: str


class Allergen(BaseModel):
    """Allergen information."""

    code: str
    display_name: str
    contains: str  # YES, NO, UNKNOWN, CAN_CONTAIN_TRACES


class PriceHistory(BaseModel):
    """Historical price data."""

    date: datetime
    price: float


class Category(BaseModel):
    """Product category."""

    id: int
    name: str
    depth: int | None = None


class Product(BaseModel):
    """Product information from Kassal.app API."""

    model_config = {"extra": "ignore"}  # Ignore extra fields from API

    id: int
    name: str
    brand: str | None = None
    vendor: str | None = None
    ean: str | None = None
    url: str | None = None
    image: str | None = None
    description: str | None = None
    ingredients: str | None = None

    current_price: float | None = None
    current_unit_price: float | None = None
    weight: float | None = None
    weight_unit: str | None = None

    category: list[Category] | None = None  # List of categories or None
    store: Store | None = None  # Single store object, not a list
    nutrition: list[NutritionItem] = Field(default_factory=list)
    allergens: list[Allergen] = Field(default_factory=list)
    price_history: list[PriceHistory] = Field(default_factory=list)

    @property
    def is_high_protein(self) -> bool:
        """Check if product has high protein content (>10g per 100g)."""
        for item in self.nutrition:
            if item.code == "PROTEIN" and item.amount > 10:
                return True
        return False

    @property
    def protein_per_100g(self) -> float | None:
        """Get protein content per 100g."""
        for item in self.nutrition:
            if item.code == "PROTEIN":
                return item.amount
        return None

    @property
    def is_on_sale(self) -> bool:
        """Check if product is currently on sale (price lower than recent average)."""
        if not self.price_history or not self.current_price:
            return False

        recent_prices = [p.price for p in self.price_history[-10:]]
        avg_price = sum(recent_prices) / len(recent_prices)
        return self.current_price < avg_price * 0.9  # 10% discount threshold


class PaginationMeta(BaseModel):
    """Pagination metadata from Kassal.app API."""

    current_page: int
    per_page: int
    from_: int | None = Field(None, alias="from")
    to: int | None = None
    path: str | None = None


class ProductSearch(BaseModel):
    """Search results from Kassal.app API."""

    data: list[Product]
    meta: PaginationMeta
    links: dict[str, str | None] = Field(default_factory=dict)

    @property
    def current_page(self) -> int:
        """Get current page number."""
        return self.meta.current_page

    @property
    def size(self) -> int:
        """Get page size."""
        return self.meta.per_page

    @property
    def total(self) -> int:
        """Get total results (estimated from current page)."""
        return self.meta.to or 0


class ProductSearchParams(BaseModel):
    """Parameters for product search."""

    search: str | None = None
    store: str | None = None  # Optional store filter
    brand: str | None = None
    category: str | None = None
    price_min: float | None = None
    price_max: float | None = None
    sort: str = "price_asc"  # price_asc, price_desc, name_asc, name_desc
    size: int = 20
    page: int = 1
    unique: bool = True  # Collapse duplicates by EAN
    excl_allergens: list[str] | None = None
    has_labels: list[str] | None = None
