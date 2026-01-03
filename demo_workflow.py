"""Complete workflow demonstration for Oda Meal Planner."""

import asyncio
from datetime import datetime, timedelta

from src.config import settings
from src.database.db import Database
from src.oda.recipes import OdaRecipeScraper
from src.oda.cart import OdaCartManager
from src.kassal.client import KassalClient
from src.kassal.models import ProductSearchParams


async def demo_complete_workflow():
    """Demonstrate the complete meal planning workflow."""
    print("\n" + "=" * 70)
    print("🍽️  Oda Meal Planner - Complete Workflow Demo")
    print("=" * 70)

    # Initialize database
    db = Database()

    # Step 1: Browse and scrape recipes from Oda.no
    print("\n📖 Step 1: Browsing Oda.no Recipes")
    print("-" * 70)

    async with OdaRecipeScraper(
        email=settings.oda_email,
        password=settings.oda_password,
        headless=False
    ) as recipe_manager:
        print("🔐 Logging in to Oda.no...")
        await recipe_manager.login()

        print("🔍 Searching for family-friendly recipes...")

        # Search for family-friendly recipes
        recipes = await recipe_manager.search_recipes(
            family_friendly=True,
            limit=5
        )

        print(f"✅ Found {len(recipes)} recipes\n")

        # Save recipes to database
        for i, recipe in enumerate(recipes, 1):
            db.save_recipe(recipe)
            print(f"   {i}. {recipe.title}")
            print(f"      URL: {recipe.url}")
            print(f"      Servings: {recipe.servings}")
            if recipe.prep_time:
                print(f"      Prep time: {recipe.prep_time}")
            print()

        # Show recipe preview
        print("🌐 Opening browser to preview recipes...")
        print("   (Browser will pause - click Resume in Playwright Inspector when done)")
        await recipe_manager.preview_recipes_page(pause=True)

    # Step 2: Create a meal plan
    print("\n📅 Step 2: Creating Weekly Meal Plan")
    print("-" * 70)

    # Get saved recipes from database
    saved_recipes = db.get_all_recipes(limit=3)

    if len(saved_recipes) < 3:
        print("⚠️  Not enough recipes saved. Skipping meal plan creation.")
    else:
        # Create a 3-day meal plan
        start_date = datetime.now()
        recipe_ids = [r.id for r in saved_recipes[:3]]

        meal_plan = db.create_meal_plan(
            name="Test Week Plan",
            start_date=start_date,
            recipe_ids=recipe_ids
        )

        print(f"✅ Created meal plan: {meal_plan.name}")
        print(f"   Start date: {meal_plan.start_date.strftime('%Y-%m-%d')}\n")

        for i, meal in enumerate(meal_plan.meals, 1):
            day = (start_date + timedelta(days=i-1)).strftime('%A')
            print(f"   Day {i} ({day}): {meal.recipe.title}")

        # Step 3: Generate shopping list
        print("\n🛒 Step 3: Generating Shopping List")
        print("-" * 70)

        shopping_list = db.create_shopping_list_from_plan(meal_plan.id)

        if shopping_list and shopping_list.items:
            print(f"✅ Shopping list created with {len(shopping_list.items)} items\n")

            for item in shopping_list.items[:10]:  # Show first 10 items
                status = "✓" if item.purchased else "○"
                print(f"   [{status}] {item.ingredient}")

            if len(shopping_list.items) > 10:
                print(f"   ... and {len(shopping_list.items) - 10} more items")
        else:
            print("⚠️  No shopping list items generated")

    # Step 4: Search products in Kassal API
    print("\n\n🔍 Step 4: Searching Products via Kassal.app API")
    print("-" * 70)

    async with KassalClient(api_key=settings.kassal_api_key) as client:
        # Search for common ingredients
        search_terms = ["kylling", "pasta", "tomat"]

        for term in search_terms:
            params = ProductSearchParams(search=term, size=2)
            results = await client.search_products(params)

            if results.data:
                print(f"\n🔎 '{term}' - Found {len(results.data)} products:")
                for product in results.data:
                    price_str = f"{product.current_price} kr" if product.current_price else "N/A"
                    print(f"   • {product.name}")
                    print(f"     Brand: {product.brand or 'N/A'} | Price: {price_str}")

    # Step 5: Add products to Oda cart
    print("\n\n🛒 Step 5: Adding Products to Oda.no Cart")
    print("-" * 70)

    async with OdaCartManager(
        email=settings.oda_email,
        password=settings.oda_password,
        headless=False
    ) as cart:
        await cart.login()

        # Add a couple of test products
        test_products = ["melk", "brød"]

        for product_name in test_products:
            print(f"\n📦 Adding '{product_name}' to cart...")
            success = await cart.add_product_by_search(product_name, quantity=1)

            if success:
                print(f"   ✅ {product_name} added successfully")
            else:
                print(f"   ❌ Failed to add {product_name}")

        # Preview the cart
        print("\n\n👁️  Opening cart preview...")
        print("   Browser will show your cart - click Resume when ready to continue")
        await cart.preview_cart(pause=True)

        # Get cart summary
        print("\n📊 Cart Summary:")
        print("-" * 70)
        items = await cart.get_cart_items()

        if items:
            print(f"✅ Cart contains {len(items)} item(s):\n")
            for i, item in enumerate(items, 1):
                print(f"   {i}. {item['name']}")
                print(f"      Quantity: {item['quantity']}")
                print(f"      Price: {item['price']}")
        else:
            print("⚠️  Could not retrieve cart items (may need selector updates)")

    # Step 6: Recipe favorites and history
    print("\n\n⭐ Step 6: Recipe Favorites & History")
    print("-" * 70)

    if saved_recipes:
        # Mark first recipe as favorite
        first_recipe = saved_recipes[0]
        db.mark_as_favorite(first_recipe.id, is_favorite=True)
        db.rate_recipe(first_recipe.id, rating=5, notes="Absolutt favoritt!")

        print(f"✅ Marked '{first_recipe.title}' as favorite with 5 stars\n")

        # Show favorites
        favorites = db.get_favorites(limit=5)
        print(f"⭐ Your Favorites ({len(favorites)}):")
        for fav in favorites:
            stars = "⭐" * (fav.rating or 0)
            print(f"   • {fav.title} {stars}")
            if fav.notes:
                print(f"     Note: {fav.notes}")

        # Show history
        history = db.get_recipe_history(limit=5)
        print(f"\n📜 Recently Used Recipes ({len(history)}):")
        for recipe in history:
            times = recipe.times_used or 0
            print(f"   • {recipe.title} (used {times}x)")

    # Final summary
    print("\n\n" + "=" * 70)
    print("🎉 Workflow Demo Complete!")
    print("=" * 70)
    print("\n✅ Demonstrated:")
    print("   • Recipe browsing and scraping from Oda.no")
    print("   • Visual recipe preview in browser")
    print("   • Meal plan creation")
    print("   • Shopping list generation")
    print("   • Product search via Kassal.app API")
    print("   • Adding products to Oda cart")
    print("   • Visual cart preview")
    print("   • Recipe favorites and rating system")
    print("   • Recipe usage history tracking")
    print("\n📝 Note: This system provides the shopping list and cart setup.")
    print("   Final checkout must be completed manually by you in the browser.")
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    asyncio.run(demo_complete_workflow())
