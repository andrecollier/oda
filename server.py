"""MCP Server for Oda Meal Planner.

This server provides tools for Claude Code to interact with Oda.no
for meal planning, recipe discovery, and grocery shopping.
"""

import asyncio
import json
from datetime import datetime
from typing import Any

from mcp.server import Server
from mcp.types import Tool, TextContent

from src.config import settings
from src.kassal import KassalClient, ProductSearchParams
from src.oda import OdaRecipeScraper, OdaCartManager, OdaOrderScraper, Recipe
from src.database import Database
from src.optimizer import MealOptimizer

# Initialize server
app = Server("oda-meal-planner")

# Initialize services
db = Database(settings.database_url)
optimizer = MealOptimizer(
    protein_goal_per_meal=settings.protein_goal_per_meal,
    prefer_family_friendly=settings.child_friendly_mode,
    prefer_meal_prep=settings.meal_prep_mode,
)


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools."""
    return [
        Tool(
            name="search_products",
            description="Search for products on Oda.no using Kassal.app API. "
            "Filter by price, category, nutrition, allergens. Returns product details with prices.",
            inputSchema={
                "type": "object",
                "properties": {
                    "search": {"type": "string", "description": "Search keyword"},
                    "category": {"type": "string", "description": "Product category"},
                    "price_max": {"type": "number", "description": "Maximum price"},
                    "sort": {
                        "type": "string",
                        "enum": ["price_asc", "price_desc", "name_asc", "name_desc"],
                        "default": "price_asc",
                    },
                    "limit": {"type": "integer", "default": 20},
                },
            },
        ),
        Tool(
            name="find_deals",
            description="Find products currently on sale/discount on Oda.no. "
            "Identifies deals by comparing current price to historical average.",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Optional category filter (e.g., 'vegetables', 'meat')",
                    },
                    "min_discount": {
                        "type": "number",
                        "default": 0.1,
                        "description": "Minimum discount percentage (0.1 = 10%)",
                    },
                },
            },
        ),
        Tool(
            name="find_high_protein_products",
            description="Find products with high protein content (>15g per 100g). "
            "Useful for planning protein-rich meals for adults.",
            inputSchema={
                "type": "object",
                "properties": {
                    "search": {
                        "type": "string",
                        "description": "Optional search term (e.g., 'chicken', 'fish')",
                    },
                    "min_protein": {
                        "type": "number",
                        "default": 15.0,
                        "description": "Minimum protein per 100g",
                    },
                },
            },
        ),
        Tool(
            name="search_recipes",
            description="Search for recipes on Oda.no. Filter by keywords, family-friendly, "
            "high-protein, meal-prep friendly, quick (fast cooking time), easy (low difficulty). "
            "Uses browser automation to scrape Oda.no.",
            inputSchema={
                "type": "object",
                "properties": {
                    "keywords": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Keywords to search for (e.g., ['kylling', 'brokkoli'])",
                    },
                    "family_friendly": {
                        "type": "boolean",
                        "default": True,
                        "description": "Filter for family/child-friendly recipes",
                    },
                    "high_protein": {
                        "type": "boolean",
                        "default": False,
                        "description": "Filter for high-protein recipes (>25g per serving)",
                    },
                    "meal_prep": {
                        "type": "boolean",
                        "default": True,
                        "description": "Filter for meal-prep friendly recipes",
                    },
                    "quick_and_easy": {
                        "type": "boolean",
                        "default": False,
                        "description": "Filter for quick and easy recipes (fast cooking, low difficulty)",
                    },
                    "limit": {"type": "integer", "default": 10},
                },
            },
        ),
        Tool(
            name="get_favorites",
            description="Get your favorite recipes that you've marked as favorites. "
            "Shows recipes you loved and want to make again.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "default": 20},
                },
            },
        ),
        Tool(
            name="get_recipe_history",
            description="Get recently used recipes from your meal planning history. "
            "See what you've made recently.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "default": 20},
                },
            },
        ),
        Tool(
            name="get_popular_recipes",
            description="Get your most frequently used recipes. "
            "See what recipes you make most often.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "default": 20},
                },
            },
        ),
        Tool(
            name="mark_favorite",
            description="Mark a recipe as favorite or remove from favorites.",
            inputSchema={
                "type": "object",
                "properties": {
                    "recipe_id": {"type": "string", "description": "Recipe ID"},
                    "is_favorite": {
                        "type": "boolean",
                        "default": True,
                        "description": "True to favorite, False to unfavorite",
                    },
                },
                "required": ["recipe_id"],
            },
        ),
        Tool(
            name="rate_recipe",
            description="Rate a recipe (1-5 stars) and optionally add notes about it.",
            inputSchema={
                "type": "object",
                "properties": {
                    "recipe_id": {"type": "string", "description": "Recipe ID"},
                    "rating": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 5,
                        "description": "Rating (1-5 stars)",
                    },
                    "notes": {
                        "type": "string",
                        "description": "Optional notes (e.g., 'Barna elsket dette!', 'Brukte litt mer salt')",
                    },
                },
                "required": ["recipe_id", "rating"],
            },
        ),
        Tool(
            name="create_meal_plan",
            description="Create an optimized weekly meal plan from selected recipes. "
            "Optimizes for ingredient reuse (especially vegetables) and nutritional goals.",
            inputSchema={
                "type": "object",
                "properties": {
                    "recipe_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of recipe IDs to include in plan",
                    },
                    "num_days": {
                        "type": "integer",
                        "default": 5,
                        "description": "Number of days to plan (default: 5)",
                    },
                    "optimize": {
                        "type": "boolean",
                        "default": True,
                        "description": "Apply optimizer to maximize ingredient reuse",
                    },
                },
                "required": ["recipe_ids"],
            },
        ),
        Tool(
            name="get_meal_plan",
            description="Get the current meal plan for this week.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="generate_shopping_list",
            description="Generate a consolidated shopping list from the current meal plan. "
            "Groups ingredients by category and consolidates quantities.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="add_to_cart",
            description="Add products to Oda.no shopping cart. Uses browser automation. "
            "Products can be added by URL or by search term.",
            inputSchema={
                "type": "object",
                "properties": {
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "url": {"type": "string"},
                                "quantity": {"type": "integer", "default": 1},
                            },
                        },
                        "description": "List of items to add (name OR url required)",
                    }
                },
                "required": ["items"],
            },
        ),
        Tool(
            name="view_cart",
            description="View items currently in Oda.no shopping cart.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="checkout_guardrail",
            description="Prepare for checkout - shows cart summary and total price. "
            "STOPS before completing purchase. User must manually complete checkout in browser.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="analyze_meal_plan",
            description="Analyze ingredient overlap and reuse in current meal plan. "
            "Shows which vegetables are used multiple times for optimization.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="preview_cart",
            description="Open browser window showing Oda.no shopping cart visually. "
            "Browser stays open for user to review products, prices, and make changes. "
            "Perfect for visual confirmation before checkout.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="preview_recipes",
            description="Open browser window showing Oda.no recipes page. "
            "Allows user to visually browse and explore recipes with images and filters. "
            "Browser stays open for manual exploration.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="preview_recipe",
            description="Open browser window showing a specific recipe with full details, "
            "images, ingredients, and cooking instructions. Browser stays open.",
            inputSchema={
                "type": "object",
                "properties": {
                    "recipe_url": {
                        "type": "string",
                        "description": "URL to the Oda.no recipe page",
                    }
                },
                "required": ["recipe_url"],
            },
        ),
        Tool(
            name="scrape_order_history",
            description="Scrape all historical orders from Oda account (https://oda.com/no/account/orders/). "
            "Analyzes purchase history going back to 2017. Used to identify recurring items and predict stock needs.",
            inputSchema={
                "type": "object",
                "properties": {
                    "max_orders": {
                        "type": "integer",
                        "default": 100,
                        "description": "Maximum number of orders to scrape (default: 100)",
                    }
                },
            },
        ),
        Tool(
            name="analyze_recurring_items",
            description="Analyze order history to identify items that are purchased regularly (faste varer). "
            "Calculates purchase frequency, predicts when items will run out, and identifies patterns.",
            inputSchema={
                "type": "object",
                "properties": {
                    "min_purchases": {
                        "type": "integer",
                        "default": 3,
                        "description": "Minimum purchases to be considered recurring (default: 3)",
                    }
                },
            },
        ),
        Tool(
            name="get_recurring_items",
            description="Get list of regularly purchased items (faste varer) with purchase frequency and predictions.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "default": 50},
                },
            },
        ),
        Tool(
            name="get_low_stock_warnings",
            description="Get items predicted to run out soon based on purchase history. "
            "Helps ensure you don't run out of essentials like milk, bread, toothpaste, etc.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="add_recurring_to_shopping_list",
            description="Automatically add recurring items (faste varer) to current shopping list. "
            "Can add all low-stock items or specific items by name.",
            inputSchema={
                "type": "object",
                "properties": {
                    "low_stock_only": {
                        "type": "boolean",
                        "default": True,
                        "description": "Only add items predicted to run out soon (default: True)",
                    },
                    "product_names": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional: specific product names to add",
                    },
                },
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls from Claude Code."""

    try:
        if name == "search_products":
            async with KassalClient(settings.kassal_api_key) as client:
                params = ProductSearchParams(
                    search=arguments.get("search"),
                    category=arguments.get("category"),
                    price_max=arguments.get("price_max"),
                    sort=arguments.get("sort", "price_asc"),
                    size=arguments.get("limit", 20),
                )
                results = await client.search_products(params)

                output = f"Found {results.total} products:\n\n"
                for product in results.data[:10]:
                    output += f"- {product.name} ({product.brand or 'N/A'})\n"
                    output += f"  Price: {product.current_price} kr\n"
                    if product.protein_per_100g:
                        output += f"  Protein: {product.protein_per_100g}g/100g\n"
                    output += f"  URL: {product.url}\n\n"

                return [TextContent(type="text", text=output)]

        elif name == "find_deals":
            async with KassalClient(settings.kassal_api_key) as client:
                deals = await client.find_deals(
                    category=arguments.get("category"),
                    min_discount=arguments.get("min_discount", 0.1),
                )

                output = f"Found {len(deals)} products on sale:\n\n"
                for product in deals:
                    output += f"- {product.name}\n"
                    output += f"  Current: {product.current_price} kr"
                    if product.is_on_sale:
                        output += " (ON SALE!)\n"
                    output += f"  URL: {product.url}\n\n"

                return [TextContent(type="text", text=output)]

        elif name == "find_high_protein_products":
            async with KassalClient(settings.kassal_api_key) as client:
                products = await client.find_high_protein_products(
                    search=arguments.get("search"),
                    min_protein=arguments.get("min_protein", 15.0),
                )

                output = f"Found {len(products)} high-protein products:\n\n"
                for product in products:
                    output += f"- {product.name}\n"
                    output += f"  Protein: {product.protein_per_100g}g/100g\n"
                    output += f"  Price: {product.current_price} kr\n"
                    output += f"  URL: {product.url}\n\n"

                return [TextContent(type="text", text=output)]

        elif name == "search_recipes":
            async with OdaRecipeScraper(
                settings.oda_email, settings.oda_password, settings.headless_browser
            ) as scraper:
                await scraper.login()

                recipes = await scraper.search_recipes(
                    keywords=arguments.get("keywords"),
                    family_friendly=arguments.get("family_friendly", True),
                    high_protein=arguments.get("high_protein", False),
                    meal_prep=arguments.get("meal_prep", True),
                    limit=arguments.get("limit", 10),
                )

                # Save recipes to database
                for recipe in recipes:
                    db.save_recipe(recipe.model_dump())

                output = f"Found {len(recipes)} recipes:\n\n"
                for recipe in recipes:
                    output += f"- {recipe.title} (ID: {recipe.id})\n"
                    output += f"  Servings: {recipe.servings} | Time: {recipe.cooking_time}\n"
                    if recipe.protein_per_serving:
                        output += f"  Protein: {recipe.protein_per_serving}g/serving\n"
                    output += f"  Vegetables: {', '.join(recipe.main_vegetables)}\n"

                    # Add intelligent suggestions for sides and drinks
                    suggestions = recipe.suggest_sides_and_drinks()
                    if suggestions.get('sides'):
                        output += f"  Forslag tilbehør: {', '.join(suggestions['sides'])}\n"
                    if suggestions.get('drinks'):
                        output += f"  Forslag drikke: {', '.join(suggestions['drinks'])}\n"

                    output += f"  URL: {recipe.url}\n\n"

                return [TextContent(type="text", text=output)]

        elif name == "create_meal_plan":
            recipe_ids = arguments["recipe_ids"]
            num_days = arguments.get("num_days", 5)
            should_optimize = arguments.get("optimize", True)

            # Load recipes from database
            recipes = [db.get_recipe(rid) for rid in recipe_ids]
            recipes = [r for r in recipes if r is not None]

            # Convert DB recipes to Recipe objects
            recipe_objs = [Recipe(**r.__dict__) for r in recipes]

            # Optimize if requested
            if should_optimize and len(recipe_objs) > num_days:
                recipe_objs = optimizer.optimize_meal_plan(recipe_objs, num_days)

            # Save to database
            now = datetime.now()
            week_number = now.isocalendar()[1]
            year = now.year

            db.clear_meal_plan(week_number, year)

            for day, recipe in enumerate(recipe_objs[:num_days]):
                db.create_meal_plan(recipe.id, day, week_number, year)

            # Analyze plan
            analysis = optimizer.analyze_ingredient_overlap(recipe_objs[:num_days])

            output = f"Created meal plan for {num_days} days (Week {week_number}, {year}):\n\n"
            for day, recipe in enumerate(recipe_objs[:num_days]):
                days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                output += f"{days[day]}: {recipe.title}\n"

            output += f"\n\nIngredient Reuse Analysis:\n"
            output += f"- Total vegetables needed: {analysis['total_vegetable_items']}\n"
            output += f"- Unique vegetables: {analysis['unique_vegetables']}\n"
            output += f"- Reuse ratio: {analysis['vegetable_reuse_ratio']:.1%}\n"
            output += f"\nMost common vegetables:\n"
            for veg, count in analysis["most_common_vegetables"]:
                output += f"  - {veg}: {count} meals\n"

            return [TextContent(type="text", text=output)]

        elif name == "get_meal_plan":
            now = datetime.now()
            week_number = now.isocalendar()[1]
            year = now.year

            meal_plans = db.get_meal_plan(week_number, year)

            if not meal_plans:
                return [TextContent(type="text", text="No meal plan for this week yet.")]

            output = f"Meal Plan for Week {week_number}, {year}:\n\n"
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

            for plan in meal_plans:
                recipe = db.get_recipe(plan.recipe_id)
                if recipe:
                    output += f"{days[plan.day_of_week]}: {recipe.title}\n"
                    output += f"  Servings: {plan.servings}\n"
                    output += f"  URL: {recipe.url}\n\n"

            return [TextContent(type="text", text=output)]

        elif name == "generate_shopping_list":
            now = datetime.now()
            week_number = now.isocalendar()[1]
            year = now.year

            meal_plans = db.get_meal_plan(week_number, year)

            if not meal_plans:
                return [TextContent(type="text", text="No meal plan for this week yet.")]

            # Load recipes
            recipes = [db.get_recipe(plan.recipe_id) for plan in meal_plans]
            recipes = [r for r in recipes if r is not None]
            recipe_objs = [Recipe(**r.__dict__) for r in recipes]

            # Generate shopping list
            shopping_list = optimizer.generate_shopping_list(recipe_objs)

            # Clear old shopping list and save new one
            db.clear_shopping_list(week_number, year)

            for category, items in shopping_list.items():
                for item in items:
                    db.add_to_shopping_list(
                        name=item["name"],
                        quantity=item["quantity"],
                        week_number=week_number,
                        year=year,
                        category=category,
                        oda_product_url=item.get("product_url"),
                    )

            # Format output
            output = f"Shopping List for Week {week_number}:\n\n"
            for category, items in shopping_list.items():
                output += f"{category}:\n"
                for item in items:
                    output += f"  - {item['name']}: {item['quantity']}"
                    if item["count"] > 1:
                        output += f" (used in {item['count']} recipes)"
                    output += "\n"
                output += "\n"

            return [TextContent(type="text", text=output)]

        elif name == "add_to_cart":
            items = arguments["items"]

            async with OdaCartManager(
                settings.oda_email, settings.oda_password, settings.headless_browser
            ) as cart:
                await cart.login()

                results = []
                for item in items:
                    if "url" in item:
                        success = await cart.add_product_by_url(
                            item["url"], item.get("quantity", 1)
                        )
                    else:
                        success = await cart.add_product_by_search(
                            item["name"], item.get("quantity", 1)
                        )

                    results.append(
                        {
                            "item": item.get("name", item.get("url")),
                            "success": success,
                        }
                    )

                output = "Added to cart:\n\n"
                for result in results:
                    status = "✓" if result["success"] else "✗"
                    output += f"{status} {result['item']}\n"

                return [TextContent(type="text", text=output)]

        elif name == "view_cart":
            async with OdaCartManager(
                settings.oda_email, settings.oda_password, settings.headless_browser
            ) as cart:
                await cart.login()
                items = await cart.get_cart_items()

                output = "Current Shopping Cart:\n\n"
                for item in items:
                    output += f"- {item['name']}\n"
                    output += f"  Quantity: {item['quantity']}\n"
                    output += f"  Price: {item['price']}\n\n"

                if not items:
                    output = "Cart is empty."

                return [TextContent(type="text", text=output)]

        elif name == "checkout_guardrail":
            async with OdaCartManager(
                settings.oda_email, settings.oda_password, settings.headless_browser
            ) as cart:
                await cart.login()
                summary = await cart.checkout_guardrail()

                output = "🛒 CHECKOUT GUARDRAIL - REVIEW BEFORE PURCHASE\n\n"
                output += f"Total Price: {summary['total_price']}\n\n"
                output += "Items in cart:\n"
                for item in summary["items"]:
                    output += f"- {item['name']} ({item['quantity']}) - {item['price']}\n"

                output += f"\n\n⚠️ {summary['message']}\n"
                output += "Browser is now on checkout page. Please complete purchase manually.\n"

                return [TextContent(type="text", text=output)]

        elif name == "analyze_meal_plan":
            now = datetime.now()
            week_number = now.isocalendar()[1]
            year = now.year

            meal_plans = db.get_meal_plan(week_number, year)

            if not meal_plans:
                return [TextContent(type="text", text="No meal plan for this week yet.")]

            recipes = [db.get_recipe(plan.recipe_id) for plan in meal_plans]
            recipes = [r for r in recipes if r is not None]
            recipe_objs = [Recipe(**r.__dict__) for r in recipes]

            analysis = optimizer.analyze_ingredient_overlap(recipe_objs)

            output = f"Meal Plan Analysis:\n\n"
            output += f"Total recipes: {analysis['total_recipes']}\n"
            output += f"Vegetable reuse ratio: {analysis['vegetable_reuse_ratio']:.1%}\n\n"

            output += "Most used vegetables:\n"
            for veg, count in analysis["most_common_vegetables"]:
                output += f"  - {veg}: {count} recipes\n"

            output += "\n\nMost common ingredients:\n"
            for ing, count in analysis["most_common_ingredients"]:
                output += f"  - {ing}: {count} times\n"

            return [TextContent(type="text", text=output)]

        elif name == "preview_cart":
            async with OdaCartManager(
                settings.oda_email, settings.oda_password, headless=False  # Force visible browser
            ) as cart:
                await cart.login()
                message = await cart.preview_cart(pause=True)
                # Browser paused with Inspector - will close when user resumes
                return [TextContent(type="text", text=message)]

        elif name == "preview_recipes":
            async with OdaRecipeScraper(
                settings.oda_email, settings.oda_password, headless=False  # Force visible browser
            ) as scraper:
                await scraper.login()
                message = await scraper.preview_recipes_page(pause=True)
                # Browser paused with Inspector - will close when user resumes
                return [TextContent(type="text", text=message)]

        elif name == "preview_recipe":
            recipe_url = arguments.get("recipe_url")

            async with OdaRecipeScraper(
                settings.oda_email, settings.oda_password, headless=False  # Force visible browser
            ) as scraper:
                await scraper.login()
                message = await scraper.preview_recipe(recipe_url, pause=True)
                # Browser paused with Inspector - will close when user resumes
                return [TextContent(type="text", text=message)]

        elif name == "get_favorites":
            favorites = db.get_favorites(limit=arguments.get("limit", 20))

            if not favorites:
                return [TextContent(type="text", text="No favorite recipes yet. Mark recipes as favorites to see them here!")]

            output = "⭐ Your Favorite Recipes:\n\n"
            for recipe in favorites:
                output += f"- {recipe.title} (ID: {recipe.id})\n"
                if recipe.rating:
                    output += f"  Rating: {'⭐' * recipe.rating} ({recipe.rating}/5)\n"
                output += f"  Used {recipe.times_used or 0} times\n"
                if recipe.notes:
                    output += f"  Notes: {recipe.notes}\n"
                output += f"  URL: {recipe.url}\n\n"

            return [TextContent(type="text", text=output)]

        elif name == "get_recipe_history":
            history = db.get_recipe_history(limit=arguments.get("limit", 20))

            if not history:
                return [TextContent(type="text", text="No recipe history yet. Create meal plans to build your history!")]

            output = "📜 Recently Used Recipes:\n\n"
            for recipe in history:
                output += f"- {recipe.title} (ID: {recipe.id})\n"
                output += f"  Last used: {recipe.last_used.strftime('%Y-%m-%d') if recipe.last_used else 'Never'}\n"
                output += f"  Used {recipe.times_used or 0} times total\n"
                if recipe.rating:
                    output += f"  Rating: {'⭐' * recipe.rating}\n"
                output += f"  URL: {recipe.url}\n\n"

            return [TextContent(type="text", text=output)]

        elif name == "get_popular_recipes":
            popular = db.get_popular_recipes(limit=arguments.get("limit", 20))

            if not popular:
                return [TextContent(type="text", text="No usage data yet. Create meal plans to see popular recipes!")]

            output = "🔥 Your Most Popular Recipes:\n\n"
            for recipe in popular:
                output += f"- {recipe.title} (ID: {recipe.id})\n"
                output += f"  Used {recipe.times_used} times\n"
                if recipe.rating:
                    output += f"  Rating: {'⭐' * recipe.rating}\n"
                output += f"  URL: {recipe.url}\n\n"

            return [TextContent(type="text", text=output)]

        elif name == "mark_favorite":
            recipe_id = arguments["recipe_id"]
            is_favorite = arguments.get("is_favorite", True)

            db.mark_as_favorite(recipe_id, is_favorite)

            action = "added to" if is_favorite else "removed from"
            output = f"✅ Recipe {recipe_id} {action} favorites!"

            return [TextContent(type="text", text=output)]

        elif name == "rate_recipe":
            recipe_id = arguments["recipe_id"]
            rating = arguments["rating"]
            notes = arguments.get("notes")

            db.rate_recipe(recipe_id, rating, notes)

            output = f"✅ Recipe {recipe_id} rated {'⭐' * rating} ({rating}/5)"
            if notes:
                output += f"\n📝 Notes saved: {notes}"

            return [TextContent(type="text", text=output)]

        elif name == "scrape_order_history":
            max_orders = arguments.get("max_orders", 100)

            async with OdaOrderScraper(
                settings.oda_email, settings.oda_password, settings.headless_browser
            ) as scraper:
                await scraper.login()
                orders = await scraper.scrape_orders(max_orders=max_orders)

                # Save orders to database
                saved_count = 0
                for order in orders:
                    db.save_order(order)
                    saved_count += 1

                output = f"✅ Successfully scraped and saved {saved_count} orders!\n\n"
                output += f"Total orders found: {len(orders)}\n"
                output += f"Date range: {orders[-1]['order_date'].strftime('%Y-%m-%d') if orders and orders[-1]['order_date'] else 'N/A'} "
                output += f"to {orders[0]['order_date'].strftime('%Y-%m-%d') if orders and orders[0]['order_date'] else 'N/A'}\n\n"
                output += f"Next step: Run 'analyze_recurring_items' to identify your faste varer!"

                return [TextContent(type="text", text=output)]

        elif name == "analyze_recurring_items":
            min_purchases = arguments.get("min_purchases", 3)

            recurring_items = db.analyze_recurring_items(min_purchases=min_purchases)

            if not recurring_items:
                return [TextContent(type="text", text="No recurring items found. Try lowering min_purchases or scrape more order history.")]

            output = f"📊 Identified {len(recurring_items)} recurring items (faste varer):\n\n"

            # Group by category (heuristic)
            categorized = {"Dairy": [], "Bread": [], "Household": [], "Other": []}

            for item in recurring_items[:20]:  # Show top 20
                product_lower = item.product_name.lower()
                if any(word in product_lower for word in ['melk', 'yoghurt', 'ost', 'smør']):
                    category = "Dairy"
                elif any(word in product_lower for word in ['brød', 'loff', 'rundstykker']):
                    category = "Bread"
                elif any(word in product_lower for word in ['såpe', 'shampo', 'tannkrem', 'papir']):
                    category = "Household"
                else:
                    category = "Other"

                categorized[category].append(item)

            for category, items in categorized.items():
                if items:
                    output += f"\n{category}:\n"
                    for item in items[:10]:
                        output += f"  • {item.product_name}\n"
                        output += f"    Purchased {item.purchase_count} times | Avg every {int(item.avg_days_between_purchase)} days\n"
                        if item.is_low_stock_warning:
                            output += f"    ⚠️ LOW STOCK: Predicted to need soon!\n"

            output += f"\n\n💡 Use 'get_low_stock_warnings' to see items running low!"
            output += f"\n💡 Use 'add_recurring_to_shopping_list' to auto-add to your list!"

            return [TextContent(type="text", text=output)]

        elif name == "get_recurring_items":
            limit = arguments.get("limit", 50)
            items = db.get_recurring_items(limit=limit)

            if not items:
                return [TextContent(type="text", text="No recurring items found. Run 'analyze_recurring_items' first!")]

            output = f"📦 Your Recurring Items (Faste Varer):\n\n"
            for item in items:
                output += f"- {item.product_name}\n"
                output += f"  Purchased: {item.purchase_count} times\n"
                output += f"  Frequency: Every {int(item.avg_days_between_purchase)} days\n"
                output += f"  Last bought: {item.last_purchase.strftime('%Y-%m-%d') if item.last_purchase else 'Unknown'}\n"

                if item.next_predicted_purchase:
                    days_until = (item.next_predicted_purchase - datetime.now()).days
                    output += f"  Next purchase predicted: in {days_until} days"
                    if item.is_low_stock_warning:
                        output += " ⚠️ SOON!"
                    output += "\n"

                output += "\n"

            return [TextContent(type="text", text=output)]

        elif name == "get_low_stock_warnings":
            items = db.get_low_stock_items()

            if not items:
                return [TextContent(type="text", text="✅ No low stock warnings! All your recurring items are well-stocked.")]

            output = f"⚠️ Low Stock Warnings - {len(items)} items need attention:\n\n"
            for item in items:
                days_until = (item.next_predicted_purchase - datetime.now()).days
                output += f"🔴 {item.product_name}\n"
                output += f"   Last purchased: {item.last_purchase.strftime('%Y-%m-%d') if item.last_purchase else 'Unknown'}\n"
                output += f"   Predicted need: in {days_until} days\n"
                output += f"   Typical purchase: Every {int(item.avg_days_between_purchase)} days\n\n"

            output += f"\n💡 Add these to your shopping list with 'add_recurring_to_shopping_list'!"

            return [TextContent(type="text", text=output)]

        elif name == "add_recurring_to_shopping_list":
            low_stock_only = arguments.get("low_stock_only", True)
            product_names = arguments.get("product_names")

            now = datetime.now()
            week_number = now.isocalendar()[1]
            year = now.year

            # Get items to add
            if product_names:
                # Add specific items
                items_to_add = []
                for name in product_names:
                    item = db.get_session().query(db.RecurringItem).filter(
                        func.lower(db.RecurringItem.product_name) == name.lower()
                    ).first()
                    if item:
                        items_to_add.append(item)
            elif low_stock_only:
                # Add only low stock items
                items_to_add = db.get_low_stock_items()
            else:
                # Add all recurring items with auto_add enabled
                items_to_add = [
                    item for item in db.get_recurring_items(limit=100)
                    if item.auto_add_to_list
                ]

            if not items_to_add:
                return [TextContent(type="text", text="No items to add. Either no low stock items found or no items selected.")]

            # Add to shopping list
            added_count = 0
            for item in items_to_add:
                db.add_to_shopping_list(
                    name=item.product_name,
                    quantity=f"{item.preferred_quantity or item.typical_quantity} stk",
                    week_number=week_number,
                    year=year,
                    category="Faste varer"
                )
                added_count += 1

            output = f"✅ Added {added_count} recurring items to shopping list (Week {week_number}):\n\n"
            for item in items_to_add[:20]:
                output += f"  • {item.product_name} ({item.preferred_quantity or item.typical_quantity} stk)\n"

            output += f"\n💡 View with 'generate_shopping_list' or add to cart with 'add_to_cart'!"

            return [TextContent(type="text", text=output)]

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    """Run the MCP server."""
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
