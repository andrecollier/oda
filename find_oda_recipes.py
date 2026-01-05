#!/usr/bin/env python3
"""
Find 4 actual recipes from Oda.no:
- 1 soup (to serve with garlic bread)
- 1 rice dish
- 2 other family-friendly dishes
"""

import asyncio
from datetime import datetime
from src.config import settings
from src.oda.recipes import OdaRecipeScraper

async def main():
    print("=" * 80)
    print("🔍 SØKER ETTER 4 OPPSKRIFTER PÅ ODA.NO")
    print("=" * 80)
    print()

    async with OdaRecipeScraper(
        settings.oda_email,
        settings.oda_password,
        headless=False  # See what's happening
    ) as scraper:

        print("🔐 Logger inn...")
        success = await scraper.login()

        if not success:
            print("❌ INNLOGGING FEILET!")
            return

        print("✅ Innlogget!")
        print()

        # Get many recipe URLs
        print("📖 Henter oppskrifter fra Oda.no...")
        print("-" * 80)

        # Get recipes without filters (family_friendly filter removes too many)
        recipe_urls = await scraper.get_recipe_urls(limit=50)
        print(f"  Fant {len(recipe_urls)} oppskrifts-URLer")
        print()

        # Scrape each recipe
        recipes = []
        for i, url in enumerate(recipe_urls, 1):
            print(f"  [{i}/{len(recipe_urls)}] Scraper: {url}")
            recipe = await scraper.scrape_recipe(url)
            if recipe and recipe.ingredients:  # Only include if it has ingredients
                recipes.append(recipe)
            if len(recipes) >= 30:
                break

        print(f"✅ Fant {len(recipes)} oppskrifter!")
        print()

        # Filter for specific types
        soup_recipes = []
        rice_recipes = []
        other_recipes = []

        for recipe in recipes:
            title_lower = recipe.title.lower()

            # Check for soup
            if any(word in title_lower for word in ['suppe', 'soup']):
                soup_recipes.append(recipe)
            # Check for rice
            elif any(word in title_lower for word in ['ris', 'rice', 'risotto']):
                rice_recipes.append(recipe)
            else:
                other_recipes.append(recipe)

        print(f"📊 Kategorier:")
        print(f"  🥣 {len(soup_recipes)} supper")
        print(f"  🍚 {len(rice_recipes)} ris-retter")
        print(f"  🍽️  {len(other_recipes)} andre retter")
        print()

        # Select 4 recipes
        selected = []

        if soup_recipes:
            selected.append(soup_recipes[0])
            print(f"✅ Suppe: {soup_recipes[0].title}")
        else:
            print("⚠️  Fant ingen suppe")

        if rice_recipes:
            selected.append(rice_recipes[0])
            print(f"✅ Ris: {rice_recipes[0].title}")
        else:
            print("⚠️  Fant ingen ris-rett")

        # Add 2 more
        for recipe in other_recipes[:2]:
            selected.append(recipe)
            print(f"✅ Rett: {recipe.title}")

        print()
        print("=" * 80)
        print("💾 LAGRER OPPSKRIFTER...")
        print("=" * 80)
        print()

        # Get week number and year
        now = datetime.now()
        week_num = now.isocalendar()[1]
        year = now.year

        # Create folder structure
        import os
        folder = f"Oppskrifter/Uke {week_num} - {year}"
        os.makedirs(folder, exist_ok=True)

        # Save to file
        filename = f"{folder}/OPPSKRIFTER - {len(selected)} middager - Uke {week_num} - {year}.txt"

        with open(filename, "w", encoding="utf-8") as f:
            f.write("=" * 80 + "\n")
            f.write(f"OPPSKRIFTER - {len(selected)} MIDDAGER - UKE {week_num} - {year}\n")
            f.write("=" * 80 + "\n\n")
            f.write("🥘 ENKLE, RASKE, SUNNE OG BARNEVENNLIGE MIDDAGER\n")
            f.write("Fra Oda.no oppskrifter\n\n")
            f.write("=" * 80 + "\n\n")

            for i, recipe in enumerate(selected, 1):
                f.write(f"MIDDAG {i}: {recipe.title.upper()}\n")
                f.write("─" * 80 + "\n\n")

                f.write(f"🔗 Link: {recipe.url}\n\n")

                if recipe.servings:
                    f.write(f"👥 Porsjoner: {recipe.servings}\n")
                if recipe.cooking_time:
                    f.write(f"⏱️  Tid: {recipe.cooking_time}\n")
                f.write("\n")

                if recipe.description:
                    f.write(f"{recipe.description}\n\n")

                f.write("INGREDIENSER:\n")
                for ing in recipe.ingredients:
                    f.write(f"  - {ing.name}\n")
                    if ing.product_url:
                        f.write(f"    🛒 {ing.product_url}\n")
                f.write("\n")

                if recipe.instructions:
                    f.write("FREMGANGSMÅTE:\n")
                    for j, step in enumerate(recipe.instructions, 1):
                        f.write(f"  {j}. {step}\n")
                    f.write("\n")

                f.write("=" * 80 + "\n\n")

            f.write("\n")
            f.write("💡 TIPS:\n")
            f.write("─" * 80 + "\n")
            f.write("- Klikk på linkene for å se bilder og detaljer\n")
            f.write("- Produktlinkene går direkte til Oda.no produktsider\n")
            f.write("- Tilpass ingrediensmengder etter behov\n")
            f.write("- Gjenbruk grønnsaker på tvers av middagene\n")
            f.write("=" * 80 + "\n")

        print(f"✅ Oppskrifter lagret til:")
        print(f"   {filename}")
        print()
        print("👨‍🍳 Du kan nå sende denne filen til din samboer!")

if __name__ == "__main__":
    asyncio.run(main())
