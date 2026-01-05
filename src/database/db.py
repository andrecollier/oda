"""Database operations."""

from datetime import datetime, timedelta
from typing import Any
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, Session
from collections import defaultdict, Counter

from .models import Base, Recipe, MealPlan, ShoppingListItem, SavedDeal, Order, OrderItem, RecurringItem


class Database:
    """Database manager for meal planner."""

    def __init__(self, database_url: str = "sqlite:///./data/meal_planner.db"):
        """Initialize database.

        Args:
            database_url: SQLAlchemy database URL
        """
        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)

        # Create tables
        Base.metadata.create_all(self.engine)

    def get_session(self) -> Session:
        """Get a new database session."""
        return self.SessionLocal()

    # Recipe operations
    def save_recipe(self, recipe_data: dict[str, Any]) -> Recipe:
        """Save a recipe to the database.

        Args:
            recipe_data: Recipe data as dictionary

        Returns:
            Saved Recipe object
        """
        with self.get_session() as session:
            recipe = Recipe(**recipe_data)
            session.merge(recipe)  # Use merge to handle updates
            session.commit()
            session.refresh(recipe)
            return recipe

    def get_recipe(self, recipe_id: str) -> Recipe | None:
        """Get a recipe by ID.

        Args:
            recipe_id: Recipe ID

        Returns:
            Recipe object or None
        """
        with self.get_session() as session:
            return session.query(Recipe).filter(Recipe.id == recipe_id).first()

    def search_recipes(
        self,
        keyword: str | None = None,
        family_friendly: bool = False,
        high_protein: bool = False,
        favorites_only: bool = False,
        min_rating: int | None = None,
        max_cooking_time: str | None = None,
        difficulty: str | None = None,
        limit: int = 20,
    ) -> list[Recipe]:
        """Search for recipes in the database.

        Args:
            keyword: Search keyword
            family_friendly: Filter for family-friendly recipes
            high_protein: Filter for high-protein recipes
            favorites_only: Only show favorite recipes
            min_rating: Minimum rating (1-5)
            max_cooking_time: Maximum cooking time (e.g., "30 min")
            difficulty: Difficulty level (e.g., "Lett", "Medium")
            limit: Maximum results

        Returns:
            List of matching recipes
        """
        with self.get_session() as session:
            query = session.query(Recipe)

            if keyword:
                query = query.filter(
                    (Recipe.title.contains(keyword))
                    | (Recipe.description.contains(keyword))
                )

            if high_protein:
                query = query.filter(Recipe.protein_per_serving >= 25)

            if favorites_only:
                query = query.filter(Recipe.is_favorite == True)

            if min_rating:
                query = query.filter(Recipe.rating >= min_rating)

            if max_cooking_time:
                query = query.filter(Recipe.cooking_time == max_cooking_time)

            if difficulty:
                query = query.filter(Recipe.difficulty == difficulty)

            query = query.limit(limit)
            return query.all()

    def mark_as_favorite(self, recipe_id: str, is_favorite: bool = True):
        """Mark a recipe as favorite.

        Args:
            recipe_id: Recipe ID
            is_favorite: True to favorite, False to unfavorite
        """
        with self.get_session() as session:
            recipe = session.query(Recipe).filter(Recipe.id == recipe_id).first()
            if recipe:
                recipe.is_favorite = is_favorite
                session.commit()

    def rate_recipe(self, recipe_id: str, rating: int, notes: str | None = None):
        """Rate a recipe and optionally add notes.

        Args:
            recipe_id: Recipe ID
            rating: Rating (1-5 stars)
            notes: Optional notes about the recipe
        """
        with self.get_session() as session:
            recipe = session.query(Recipe).filter(Recipe.id == recipe_id).first()
            if recipe:
                recipe.rating = max(1, min(5, rating))  # Ensure 1-5
                if notes:
                    recipe.notes = notes
                session.commit()

    def get_favorites(self, limit: int = 20) -> list[Recipe]:
        """Get favorite recipes.

        Args:
            limit: Maximum results

        Returns:
            List of favorite recipes
        """
        with self.get_session() as session:
            return (
                session.query(Recipe)
                .filter(Recipe.is_favorite == True)
                .order_by(Recipe.rating.desc(), Recipe.times_used.desc())
                .limit(limit)
                .all()
            )

    def get_recipe_history(self, limit: int = 20) -> list[Recipe]:
        """Get recently used recipes.

        Args:
            limit: Maximum results

        Returns:
            List of recipes ordered by last use
        """
        with self.get_session() as session:
            return (
                session.query(Recipe)
                .filter(Recipe.last_used.isnot(None))
                .order_by(Recipe.last_used.desc())
                .limit(limit)
                .all()
            )

    def get_popular_recipes(self, limit: int = 20) -> list[Recipe]:
        """Get most frequently used recipes.

        Args:
            limit: Maximum results

        Returns:
            List of recipes ordered by usage count
        """
        with self.get_session() as session:
            return (
                session.query(Recipe)
                .filter(Recipe.times_used > 0)
                .order_by(Recipe.times_used.desc(), Recipe.rating.desc())
                .limit(limit)
                .all()
            )

    # Meal plan operations
    def create_meal_plan(
        self, recipe_id: str, day_of_week: int, week_number: int, year: int, servings: int = 4
    ) -> MealPlan:
        """Add a recipe to the meal plan.

        Args:
            recipe_id: Recipe ID
            day_of_week: Day of week (0=Monday, 6=Sunday)
            week_number: ISO week number
            year: Year
            servings: Number of servings

        Returns:
            MealPlan object
        """
        with self.get_session() as session:
            meal_plan = MealPlan(
                recipe_id=recipe_id,
                day_of_week=day_of_week,
                week_number=week_number,
                year=year,
                servings=servings,
            )
            session.add(meal_plan)

            # Update recipe's last_used timestamp and usage count
            recipe = session.query(Recipe).filter(Recipe.id == recipe_id).first()
            if recipe:
                recipe.last_used = datetime.utcnow()
                recipe.times_used = (recipe.times_used or 0) + 1

            session.commit()
            session.refresh(meal_plan)
            return meal_plan

    def get_meal_plan(self, week_number: int, year: int) -> list[MealPlan]:
        """Get meal plan for a specific week.

        Args:
            week_number: ISO week number
            year: Year

        Returns:
            List of MealPlan objects for that week
        """
        with self.get_session() as session:
            return (
                session.query(MealPlan)
                .filter(MealPlan.week_number == week_number, MealPlan.year == year)
                .order_by(MealPlan.day_of_week)
                .all()
            )

    def clear_meal_plan(self, week_number: int, year: int):
        """Clear meal plan for a specific week.

        Args:
            week_number: ISO week number
            year: Year
        """
        with self.get_session() as session:
            session.query(MealPlan).filter(
                MealPlan.week_number == week_number, MealPlan.year == year
            ).delete()
            session.commit()

    # Shopping list operations
    def add_to_shopping_list(
        self,
        name: str,
        quantity: str,
        week_number: int,
        year: int,
        category: str | None = None,
        kassal_product_id: int | None = None,
        oda_product_url: str | None = None,
        current_price: float | None = None,
    ) -> ShoppingListItem:
        """Add item to shopping list.

        Args:
            name: Item name
            quantity: Quantity (e.g., "500g", "2 stk")
            week_number: ISO week number
            year: Year
            category: Optional category
            kassal_product_id: Optional Kassal product ID
            oda_product_url: Optional Oda product URL
            current_price: Optional current price

        Returns:
            ShoppingListItem object
        """
        with self.get_session() as session:
            item = ShoppingListItem(
                name=name,
                quantity=quantity,
                category=category,
                week_number=week_number,
                year=year,
                kassal_product_id=kassal_product_id,
                oda_product_url=oda_product_url,
                current_price=current_price,
            )
            session.add(item)
            session.commit()
            session.refresh(item)
            return item

    def get_shopping_list(self, week_number: int, year: int) -> list[ShoppingListItem]:
        """Get shopping list for a specific week.

        Args:
            week_number: ISO week number
            year: Year

        Returns:
            List of ShoppingListItem objects
        """
        with self.get_session() as session:
            return (
                session.query(ShoppingListItem)
                .filter(
                    ShoppingListItem.week_number == week_number,
                    ShoppingListItem.year == year,
                )
                .order_by(ShoppingListItem.category, ShoppingListItem.name)
                .all()
            )

    def mark_item_purchased(self, item_id: int):
        """Mark a shopping list item as purchased.

        Args:
            item_id: ShoppingListItem ID
        """
        with self.get_session() as session:
            item = session.query(ShoppingListItem).filter(ShoppingListItem.id == item_id).first()
            if item:
                item.purchased = True
                item.purchased_at = datetime.utcnow()
                session.commit()

    def mark_item_in_cart(self, item_id: int):
        """Mark a shopping list item as added to cart.

        Args:
            item_id: ShoppingListItem ID
        """
        with self.get_session() as session:
            item = session.query(ShoppingListItem).filter(ShoppingListItem.id == item_id).first()
            if item:
                item.in_cart = True
                session.commit()

    def clear_shopping_list(self, week_number: int, year: int):
        """Clear shopping list for a specific week.

        Args:
            week_number: ISO week number
            year: Year
        """
        with self.get_session() as session:
            session.query(ShoppingListItem).filter(
                ShoppingListItem.week_number == week_number, ShoppingListItem.year == year
            ).delete()
            session.commit()

    # Deal operations
    def save_deal(
        self,
        product_name: str,
        kassal_product_id: int,
        original_price: float,
        sale_price: float,
    ) -> SavedDeal:
        """Save a deal for future reference.

        Args:
            product_name: Product name
            kassal_product_id: Kassal product ID
            original_price: Original price
            sale_price: Sale price

        Returns:
            SavedDeal object
        """
        with self.get_session() as session:
            discount = ((original_price - sale_price) / original_price) * 100

            deal = SavedDeal(
                product_name=product_name,
                kassal_product_id=kassal_product_id,
                original_price=original_price,
                sale_price=sale_price,
                discount_percentage=discount,
            )
            session.add(deal)
            session.commit()
            session.refresh(deal)
            return deal

    def get_active_deals(self) -> list[SavedDeal]:
        """Get all saved deals.

        Returns:
            List of SavedDeal objects
        """
        with self.get_session() as session:
            return session.query(SavedDeal).order_by(SavedDeal.discount_percentage.desc()).all()

    # Order operations
    def save_order(self, order_data: dict[str, Any]) -> Order:
        """Save an order to the database.

        Args:
            order_data: Order data as dictionary with keys:
                - order_number
                - order_date
                - total_price
                - status
                - items (list of dicts with product_name, quantity, price)

        Returns:
            Saved Order object
        """
        with self.get_session() as session:
            # Check if order already exists
            existing = session.query(Order).filter(
                Order.order_number == order_data['order_number']
            ).first()

            if existing:
                # Update existing order
                existing.total_price = order_data.get('total_price')
                existing.status = order_data.get('status')
                order = existing
            else:
                # Create new order
                order = Order(
                    order_number=order_data['order_number'],
                    order_date=order_data['order_date'],
                    total_price=order_data.get('total_price'),
                    status=order_data.get('status', 'delivered')
                )
                session.add(order)
                session.flush()  # Get order ID

            # Add items
            for item_data in order_data.get('items', []):
                # Check if item already exists
                existing_item = session.query(OrderItem).filter(
                    OrderItem.order_id == order.id,
                    OrderItem.product_name == item_data['product_name']
                ).first()

                if not existing_item:
                    item = OrderItem(
                        order_id=order.id,
                        product_name=item_data['product_name'],
                        quantity=item_data.get('quantity', 1),
                        price_per_unit=item_data.get('price'),
                        total_price=item_data.get('price')
                    )
                    session.add(item)

            session.commit()
            session.refresh(order)
            return order

    def get_all_orders(self, limit: int = 100) -> list[Order]:
        """Get all orders sorted by date (newest first).

        Args:
            limit: Maximum number of orders to return

        Returns:
            List of Order objects
        """
        with self.get_session() as session:
            return session.query(Order).order_by(Order.order_date.desc()).limit(limit).all()

    def analyze_recurring_items(self, min_purchases: int = 3) -> list[RecurringItem]:
        """Analyze order history to identify recurring items.

        An item is considered recurring if it's been purchased at least min_purchases times.

        Args:
            min_purchases: Minimum number of purchases to be considered recurring (default: 3)

        Returns:
            List of RecurringItem objects
        """
        with self.get_session() as session:
            # Get all order items
            all_items = session.query(OrderItem).join(Order).all()

            # Group by product name
            product_purchases = defaultdict(list)

            for item in all_items:
                # Normalize product name (lowercase, strip whitespace)
                normalized_name = item.product_name.strip().lower()
                product_purchases[normalized_name].append({
                    'date': item.order.order_date,
                    'quantity': item.quantity,
                    'price': item.price_per_unit
                })

            # Analyze each product
            recurring_items = []

            for product_name, purchases in product_purchases.items():
                if len(purchases) < min_purchases:
                    continue

                # Sort by date
                purchases = sorted(purchases, key=lambda x: x['date'])

                # Calculate statistics
                purchase_count = len(purchases)
                first_purchase = purchases[0]['date']
                last_purchase = purchases[-1]['date']

                # Calculate average days between purchases
                if purchase_count > 1:
                    total_days = (last_purchase - first_purchase).days
                    avg_days = total_days / (purchase_count - 1)
                else:
                    avg_days = 30  # Default to monthly if only 1 purchase

                # Calculate typical quantity
                quantities = [p['quantity'] for p in purchases]
                typical_quantity = int(sum(quantities) / len(quantities))

                # Estimate days supply (heuristic based on product type)
                estimated_days_supply = self._estimate_product_lifespan(product_name, avg_days)

                # Predict next purchase date
                next_predicted = last_purchase + timedelta(days=int(avg_days))

                # Check if low stock warning needed (within 3 days of predicted date)
                days_until_next = (next_predicted - datetime.now()).days
                is_low_stock = days_until_next <= 3

                # Check if already exists in database
                existing = session.query(RecurringItem).filter(
                    func.lower(RecurringItem.product_name) == product_name.lower()
                ).first()

                if existing:
                    # Update existing
                    existing.purchase_count = purchase_count
                    existing.last_purchase = last_purchase
                    existing.avg_days_between_purchase = avg_days
                    existing.typical_quantity = typical_quantity
                    existing.estimated_days_supply = estimated_days_supply
                    existing.next_predicted_purchase = next_predicted
                    existing.is_low_stock_warning = is_low_stock
                    existing.updated_at = datetime.utcnow()
                    recurring_item = existing
                else:
                    # Create new
                    recurring_item = RecurringItem(
                        product_name=product_name,
                        purchase_count=purchase_count,
                        first_purchase=first_purchase,
                        last_purchase=last_purchase,
                        avg_days_between_purchase=avg_days,
                        typical_quantity=typical_quantity,
                        estimated_days_supply=estimated_days_supply,
                        next_predicted_purchase=next_predicted,
                        is_low_stock_warning=is_low_stock
                    )
                    session.add(recurring_item)

                recurring_items.append(recurring_item)

            session.commit()
            return recurring_items

    def _estimate_product_lifespan(self, product_name: str, avg_days_between: float) -> int:
        """Estimate how long a product typically lasts based on its name.

        Args:
            product_name: Product name
            avg_days_between: Average days between purchases

        Returns:
            Estimated days the product lasts
        """
        product_lower = product_name.lower()

        # Fresh products (short lifespan)
        if any(word in product_lower for word in ['melk', 'milk', 'brød', 'bread', 'salat', 'lettuce']):
            return min(7, int(avg_days_between))

        # Dairy (medium lifespan)
        if any(word in product_lower for word in ['yoghurt', 'ost', 'cheese', 'smør', 'butter']):
            return min(14, int(avg_days_between))

        # Hygiene/household (long lifespan)
        if any(word in product_lower for word in ['såpe', 'soap', 'shampo', 'tannkrem', 'toothpaste', 'papir', 'paper']):
            return int(avg_days_between * 0.9)  # Close to purchase frequency

        # Default: assume purchase frequency = consumption rate
        return int(avg_days_between)

    def get_recurring_items(self, limit: int = 50) -> list[RecurringItem]:
        """Get all recurring items ordered by purchase frequency.

        Args:
            limit: Maximum number of items to return

        Returns:
            List of RecurringItem objects
        """
        with self.get_session() as session:
            return (
                session.query(RecurringItem)
                .order_by(RecurringItem.purchase_count.desc())
                .limit(limit)
                .all()
            )

    def get_low_stock_items(self) -> list[RecurringItem]:
        """Get items that are predicted to run out soon.

        Returns:
            List of RecurringItem objects with is_low_stock_warning=True
        """
        with self.get_session() as session:
            return (
                session.query(RecurringItem)
                .filter(RecurringItem.is_low_stock_warning == True)
                .order_by(RecurringItem.next_predicted_purchase)
                .all()
            )

    def mark_recurring_auto_add(self, product_name: str, auto_add: bool = True, quantity: int = 1):
        """Mark a recurring item to be automatically added to shopping lists.

        Args:
            product_name: Product name
            auto_add: Whether to auto-add (default: True)
            quantity: Preferred quantity (default: 1)
        """
        with self.get_session() as session:
            item = session.query(RecurringItem).filter(
                func.lower(RecurringItem.product_name) == product_name.lower()
            ).first()

            if item:
                item.auto_add_to_list = auto_add
                item.preferred_quantity = quantity
                item.updated_at = datetime.utcnow()
                session.commit()
