"""Find and present weekly recipe suggestions for approval."""

import asyncio
from datetime import datetime
from src.config import settings
from src.oda.recipes import OdaRecipeScraper


async def explore_recipe_categories():
    """Explore different recipe categories on Oda.no."""
    print("\n" + "=" * 80)
    print("🍽️  Ukesmeny - Familiemiddager for Uke 1 2026")
    print("=" * 80)
    print(f"\n👨‍👩‍👧‍👦 Familie: 2 voksne + 2 barn")
    print(f"🎯 Kriterier: Barnevennlig, sunn, variert")
    print(f"📅 Dato: {datetime.now().strftime('%Y-%m-%d')}")

    # Categories to explore
    categories_to_check = [
        ("Supper", "https://oda.com/no/recipes/tags/16-soups/"),
        ("Barnevennlig", "https://oda.com/no/recipes/tags/49-barnevennlig/"),
        ("Kylling", "https://oda.com/no/recipes/tags/22-chicken/"),
        ("Rask middag", "https://oda.com/no/recipes/tags/53-quick-dinner/"),
        ("Grønnsaker", "https://oda.com/no/recipes/tags/18-vegetables/"),
    ]

    async with OdaRecipeScraper(
        email=settings.oda_email,
        password=settings.oda_password,
        headless=False
    ) as scraper:
        print("\n🔐 Logger inn på Oda.no...")
        await scraper.login()
        print("✅ Innlogget!")

        all_recipes = []

        for category_name, category_url in categories_to_check:
            print(f"\n\n{'=' * 80}")
            print(f"📂 Utforsker kategori: {category_name}")
            print(f"🔗 {category_url}")
            print("=" * 80)

            # Navigate to category
            await scraper.page.goto(category_url, wait_until="networkidle")
            await scraper.page.wait_for_timeout(2000)

            # Try to scrape recipes from this category
            print(f"🔍 Søker i {category_name}...")

            # Get recipe cards on the page
            recipe_cards = await scraper.page.query_selector_all('article, [data-testid="recipe-card"], .recipe-card, a[href*="/recipes/"]')

            print(f"📊 Fant {len(recipe_cards)} elementer på siden")

            # Extract URLs from the first few cards
            found_in_category = 0
            for card in recipe_cards[:10]:  # Check first 10
                try:
                    # Try to get href
                    href = await card.get_attribute('href')
                    if href and '/recipes/' in href and href not in [r['url'] for r in all_recipes]:
                        # Get recipe title if possible
                        title_elem = await card.query_selector('h2, h3, [class*="title"]')
                        title = await title_elem.inner_text() if title_elem else "Unknown"

                        if not href.startswith('http'):
                            href = f"https://oda.com{href}"

                        all_recipes.append({
                            'title': title.strip(),
                            'url': href,
                            'category': category_name
                        })
                        found_in_category += 1

                        if found_in_category >= 3:  # Max 3 per category
                            break
                except Exception as e:
                    continue

            print(f"✅ Fant {found_in_category} nye oppskrifter i {category_name}")

            # Small delay between categories
            await scraper.page.wait_for_timeout(1000)

        # Show all found recipes
        print("\n\n" + "=" * 80)
        print("📋 OPPSUMMERING - Alle funnet oppskrifter")
        print("=" * 80)

        if all_recipes:
            for i, recipe in enumerate(all_recipes, 1):
                print(f"\n{i}. {recipe['title']}")
                print(f"   📂 Kategori: {recipe['category']}")
                print(f"   🔗 URL: {recipe['url']}")
        else:
            print("\n⚠️  Ingen oppskrifter funnet med automatisk scraping")
            print("📝 Åpner 'Dine middager' så du kan velge manuelt...")

        # Navigate to "Dine middager" (Dinner Bank)
        print("\n\n" + "=" * 80)
        print("🏦 Åpner 'Dine middager' - Middagsbanken")
        print("=" * 80)

        dinner_bank_url = "https://oda.com/no/recipes/dinner-bank/"
        await scraper.page.goto(dinner_bank_url, wait_until="networkidle")

        print("\n🌐 Du kan nå:")
        print("  1. Bla gjennom oppskrifter")
        print("  2. Klikk på oppskrifter for å se detaljer")
        print("  3. Legg til i 'Dine middager'")
        print("  4. Opprett ny middagsliste: 'Uke 1 2026'")
        print("\n💡 Tips:")
        print("  • Klikk 'Opprett ny middagsliste' øverst")
        print("  • Gi den navnet: 'Uke 1 2026'")
        print("  • Legg til oppskrifter du vil ha")
        print("  • Handleliste genereres automatisk")

        print("\n⏸️  Nettleseren forblir åpen...")
        print("  Når du er ferdig med å velge oppskrifter, trykk Ctrl+C her")
        print("  Eller lukk nettleservinduet")

        # Keep browser open
        try:
            while True:
                await scraper.page.wait_for_timeout(10000)
        except KeyboardInterrupt:
            print("\n\n✅ Avslutter...")


if __name__ == "__main__":
    try:
        asyncio.run(explore_recipe_categories())
    except KeyboardInterrupt:
        print("\n\n👋 Hadet!")
