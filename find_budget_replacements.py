#!/usr/bin/env python3
"""Find budget replacement recipes that match ingredients in cart."""

import asyncio
from src.config import settings
from src.oda.recipes import OdaRecipeScraper


async def main():
    """Find budget-friendly replacement recipes."""
    print("="*80)
    print("🔍 SØKER ETTER BILLIGE ERSTATNINGS-OPPSKRIFTER")
    print("="*80)
    print()
    print("Ingredienser i handlekurven:")
    print("  ✓ Kjøttdeig x2")
    print("  ✓ Pølser")
    print("  ✓ Pasta")
    print("  ✓ Melk, kremfløte")
    print("  ✓ Løk, hvitløk, poteter")
    print()
    print("Søker etter oppskrifter med disse ingrediensene...")
    print()

    async with OdaRecipeScraper(
        settings.oda_email,
        settings.oda_password,
        headless=False
    ) as scraper:

        await scraper.login()
        print("✅ Innlogget!\n")

        # Search for specific budget recipes
        searches = [
            "kjøttdeig pasta",
            "kjøttboller",
            "pølse gryte",
            "lapskaus",
            "pasta bolognese",
        ]

        all_recipes = []

        for search_term in searches:
            print(f"Søker: '{search_term}'...")

            search_url = f"{scraper.BASE_URL}/recipes/?q={search_term}"
            await scraper.page.goto(search_url, wait_until="networkidle")
            await asyncio.sleep(2)

            # Get recipe links (use same selector as existing get_recipe_urls method)
            all_links = await scraper.page.query_selector_all('a[href*="/recipes/"]')

            found_count = 0
            for link in all_links[:30]:  # Check first 30 links
                try:
                    href = await link.get_attribute('href')
                    if not href:
                        continue

                    # Skip plans/categories/base recipe page - only want actual recipes
                    if any(x in href for x in ['/plans/', '/categories/', 'all', '/?', '?category']):
                        continue

                    # Only include if it's a specific recipe (has path after /recipes/)
                    if '/recipes/' in href:
                        # Extract recipe slug (e.g., /recipes/kylling-pasta-123 -> kylling-pasta-123)
                        slug = href.split('/recipes/')[-1].strip('/')
                        if not slug or slug == '':
                            continue

                        full_url = href if href.startswith('http') else f"{scraper.BASE_URL}{href}"

                        # Check if already added
                        if full_url in [r['url'] for r in all_recipes]:
                            continue

                        # Get title from link text
                        title = await link.inner_text()
                        title = title.strip()

                        if title and title not in ['Kokeboka', 'Utforsk', 'Alle oppskrifter', 'Tilbake']:
                            all_recipes.append({
                                'title': title,
                                'url': full_url,
                                'search_term': search_term
                            })
                            found_count += 1

                        if found_count >= 5:  # Stop after finding 5 per search
                            break
                except:
                    continue

            print(f"  Fant {found_count} oppskrifter\n")

        print("="*80)
        print(f"FANT {len(all_recipes)} OPPSKRIFTER")
        print("="*80)
        print()

        # Show recipes
        for i, recipe in enumerate(all_recipes[:15], 1):
            print(f"{i:2}. {recipe['title'][:70]}")
            print(f"    Fra søk: {recipe['search_term']}")
            print()

        # Now scrape details for top 3 promising ones
        print("="*80)
        print("HENTER DETALJER FOR LOVENDE OPPSKRIFTER")
        print("="*80)
        print()

        selected = []

        for recipe in all_recipes[:10]:
            try:
                print(f"Henter: {recipe['title'][:60]}...")

                details = await scraper.scrape_recipe(recipe['url'])

                if not details:
                    print(f"  ⚠️  Kunne ikke hente oppskrift - hopper over\n")
                    continue

                if not details.ingredients:
                    print(f"  ⚠️  Ingen ingredienser funnet - hopper over\n")
                    continue

                num_ing = len(details.ingredients)

                # Check for expensive ingredients
                ingredients_text = ' '.join([ing.name for ing in details.ingredients]).lower()
                expensive = ['entrecôte', 'oksefil', 'laks', 'torsk', 'kveite',
                            'svinekoteletter', 'nakkekoteletter', 'reker']

                has_expensive = any(kw in ingredients_text for kw in expensive)

                if has_expensive:
                    print(f"  ⚠️  Inneholder dyre ingredienser - hopper over\n")
                    continue

                if num_ing > 12:
                    print(f"  ⚠️  For mange ingredienser ({num_ing}) - hopper over\n")
                    continue

                print(f"  ✅ God kandidat! ({num_ing} ingredienser)")
                selected.append(details)
                print()

                if len(selected) >= 3:
                    break

                await asyncio.sleep(2)

            except Exception as e:
                print(f"  ❌ Feil: {e}\n")
                continue

        print()
        print("="*80)
        print(f"✅ VALGTE {len(selected)} BILLIGE OPPSKRIFTER")
        print("="*80)
        print()

        for i, recipe in enumerate(selected, 1):
            print(f"{i}. {recipe.title}")
            print(f"   Ingredienser: {len(recipe.ingredients)}")
            print(f"   URL: {recipe.url}")
            print()

        # Save if we found any
        if selected:
            output_file = "Oppskrifter/Uke 1 - 2026/BUDSJETT_ERSTATNINGER.txt"

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("="*80 + "\n")
                f.write("BUDSJETT ERSTATNINGS-OPPSKRIFTER\n")
                f.write("="*80 + "\n\n")

                for i, recipe in enumerate(selected, 1):
                    f.write(f"OPPSKRIFT {i}: {recipe.title.upper()}\n")
                    f.write("-"*80 + "\n\n")
                    f.write(f"🔗 Link: {recipe.url}\n\n")

                    if recipe.servings:
                        f.write(f"👥 Porsjoner: {recipe.servings}\n")
                    if recipe.cooking_time:
                        f.write(f"⏱️  Tid: {recipe.cooking_time}\n")

                    f.write("\nINGREDIENSER:\n")
                    for ing in recipe.ingredients:
                        f.write(f"  - {ing.name}\n")

                    if recipe.instructions:
                        f.write("\nFREMGANGSMÅTE:\n")
                        for j, step in enumerate(recipe.instructions, 1):
                            f.write(f"  {j}. {step}\n")

                    f.write("\n" + "="*80 + "\n\n")

            print(f"📝 Oppskrifter lagret til: {output_file}")
            print()

        print("Nettleseren holdes åpen...")
        print("Trykk Ctrl+C når du er ferdig...\n")

        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\nAvslutter...")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nAvbrutt")
