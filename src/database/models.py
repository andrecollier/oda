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


class Order(Base):
    """Historical Oda orders from account/orders page."""

    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_number = Column(String, unique=True, nullable=False)  # Oda order reference number
    order_date = Column(DateTime, nullable=False)
    delivery_date = Column(DateTime)
    total_price = Column(Float)

    # Status tracking
    status = Column(String)  # "delivered", "cancelled", etc.

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    """Individual items in an order."""

    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)

    product_name = Column(String, nullable=False)
    quantity = Column(Integer, default=1)
    price_per_unit = Column(Float)
    total_price = Column(Float)

    # Product categorization for analysis
    category = Column(String)  # "Dairy", "Bread", "Meat", etc.
    is_recurring = Column(Boolean, default=False)  # Marked as recurring item

    # For linking to current products
    oda_product_url = Column(String)

    # Relationships
    order = relationship("Order", back_populates="items")


class RecurringItem(Base):
    """Items that are regularly purchased (faste varer)."""

    __tablename__ = "recurring_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_name = Column(String, nullable=False, unique=True)

    # Purchase frequency analysis
    purchase_count = Column(Integer, default=0)  # How many times purchased total
    first_purchase = Column(DateTime)
    last_purchase = Column(DateTime)
    avg_days_between_purchase = Column(Float)  # Average days between purchases

    # Consumption estimation
    typical_quantity = Column(Integer, default=1)  # Typical quantity per purchase
    estimated_days_supply = Column(Integer)  # How many days this typically lasts

    # Product info
    category = Column(String)
    oda_product_url = Column(String)
    current_price = Column(Float)

    # User preferences
    auto_add_to_list = Column(Boolean, default=False)  # Auto-add to shopping list
    preferred_quantity = Column(Integer, default=1)  # User's preferred quantity

    # Predictions
    next_predicted_purchase = Column(DateTime)  # When we predict they'll need this next
    is_low_stock_warning = Column(Boolean, default=False)  # Currently running low

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
