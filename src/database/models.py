"""SQLAlchemy database models."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Recipe(Base):
    """Recipe stored in database."""

    __tablename__ = "recipes"

    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    image_url = Column(String)
    description = Column(Text)

    servings = Column(Integer, default=4)
    cooking_time = Column(String)
    difficulty = Column(String)

    ingredients = Column(JSON)  # List of ingredients as JSON
    instructions = Column(JSON)  # List of instructions as JSON
    categories = Column(JSON)  # List of categories
    tags = Column(JSON)  # List of tags

    protein_per_serving = Column(Float)
    calories_per_serving = Column(Float)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime)
    times_used = Column(Integer, default=0)  # How many times this recipe has been used

    # User preferences
    is_favorite = Column(Boolean, default=False)
    rating = Column(Integer)  # 1-5 stars
    notes = Column(Text)  # User notes about the recipe

    # Relationships
    meal_plans = relationship("MealPlan", back_populates="recipe")


class MealPlan(Base):
    """Weekly meal plan."""

    __tablename__ = "meal_plans"

    id = Column(Integer, primary_key=True, autoincrement=True)
    recipe_id = Column(String, ForeignKey("recipes.id"), nullable=False)

    # Which day and meal
    day_of_week = Column(Integer, nullable=False)  # 0=Monday, 6=Sunday
    meal_type = Column(String, default="dinner")  # breakfast, lunch, dinner

    # When this plan was created
    week_number = Column(Integer, nullable=False)  # ISO week number
    year = Column(Integer, nullable=False)

    servings = Column(Integer, default=4)
    notes = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    recipe = relationship("Recipe", back_populates="meal_plans")


class ShoppingListItem(Base):
    """Shopping list items."""

    __tablename__ = "shopping_list"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    quantity = Column(String)  # "500g", "2 stk", etc.
    category = Column(String)  # "Vegetables", "Meat", etc.

    # Product info from Kassal.app
    kassal_product_id = Column(Integer)
    oda_product_url = Column(String)
    current_price = Column(Float)

    # Status
    purchased = Column(Boolean, default=False)
    in_cart = Column(Boolean, default=False)

    # Which week/plan this belongs to
    week_number = Column(Integer)
    year = Column(Integer)

    created_at = Column(DateTime, default=datetime.utcnow)
    purchased_at = Column(DateTime)


class SavedDeal(Base):
    """Saved deals/offers for future reference."""

    __tablename__ = "saved_deals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_name = Column(String, nullable=False)
    kassal_product_id = Column(Integer)

    original_price = Column(Float)
    sale_price = Column(Float)
    discount_percentage = Column(Float)

    valid_from = Column(DateTime)
    valid_until = Column(DateTime)

    saved_at = Column(DateTime, default=datetime.utcnow)
