"""Find family-friendly recipes from Oda.no."""

import asyncio
from src.config import settings
from src.oda.recipes import OdaRecipeScraper
from src.database.db import Database


async def find_family_recipes():
    """Search for family-friendly recipes."""
    print("\n" + "=" * 70)
    print("🍽️  Søker etter familiemennlige oppskrifter...")
    print("=" * 70)

    db = Database()

    async with OdaRecipeScraper(
        email=settings.oda_email,
        password=settings.oda_password,
        headless=False
    ) as scraper:
        print("\n🔐 Logger inn på Oda.no...")
        await scraper.login()
        print("✅ Innlogget!\n")

        # Search for family-friendly recipes
        print("🔍 Søker etter familiemennlige oppskrifter...")
        recipes = await scraper.search_recipes(
            family_friendly=True,
            limit=20
        )

        if not recipes:
            print("⚠️  Fant ingen oppskrifter med family_friendly filter.")
            print("   Prøver generelt søk...\n")
            recipes = await scraper.search_recipes(limit=20)

        if not recipes:
            print("❌ Ingen oppskrifter funnet")
            print("\n📝 La meg åpne Oda oppskriftsiden så du kan se...")
            await scraper.preview_recipes_page(pause=False)
            await scraper.page.wait_for_timeout(10000)
            return

        print(f"✅ Fant {len(recipes)} oppskrifter!\n")
        print("=" * 70)

        # Show all recipes
        for i, recipe in enumerate(recipes, 1):
            print(f"\n{i}. {recipe.title}")
            print(f"   URL: {recipe.url}")
            if recipe.description:
                print(f"   📝 {recipe.description[:100]}...")
            if recipe.servings:
                print(f"   👥 Porsjoner: {recipe.servings}")
            if recipe.cooking_time:
                print(f"   ⏱️  Tilberedningstid: {recipe.cooking_time}")

            # Show ingredients preview
            if recipe.ingredients:
                print(f"   🥕 Ingredienser ({len(recipe.ingredients)}):")
                for ing in recipe.ingredients[:3]:
                    print(f"      - {ing.name}")
                if len(recipe.ingredients) > 3:
                    print(f"      ... og {len(recipe.ingredients) - 3} til")

            # Check if family-friendly
            if recipe.is_family_friendly:
                print(f"   ✅ Barnevennlig")

            # Save to database (convert Pydantic model to dict)
            try:
                db.save_recipe(recipe.model_dump())
            except Exception as e:
                print(f"   ⚠️  Kunne ikke lagre: {e}")

        print("\n" + "=" * 70)
        print(f"💾 Lagret {len(recipes)} oppskrifter til databasen")
        print("\n🌐 Åpner Oda oppskrifter i nettleser for visuell gjennomgang...")
        print("   (Nettleseren holder seg åpen i 30 sekunder)")

        await scraper.preview_recipes_page(pause=False)
        await scraper.page.wait_for_timeout(30000)

        print("\n" + "=" * 70)
        print("✅ Ferdig!")
        print("=" * 70)


if __name__ == "__main__":
    asyncio.run(find_family_recipes())
