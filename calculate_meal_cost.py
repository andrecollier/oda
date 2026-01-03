"""Calculate total cost for weekly meal plan."""

import asyncio
from src.config import settings
from src.oda.recipes import OdaRecipeScraper
from src.kassal.client import KassalClient
from src.kassal.models import ProductSearchParams


# Recipe URLs for Week 1 2026
RECIPES = {
    "Blomkålsuppe med krydderstekte kikerter": "https://oda.com/no/recipes/2835-oda-blomkalsuppe-med-krydderstekte-kikerter/",
    "Superenkel kylling, brokkoli og ris": "https://oda.com/no/recipes/2026-oda-superenkel-kylling-brokkoli-og-ris/",
    "Rask kremet kyllingpanne med parmesan og pasta": "https://oda.com/no/recipes/3788-silje-feiring-rask-kremet-kyllingpanne-med-parmesan-og-pasta/",
    "Pasta bolognese": "https://oda.com/no/recipes/4519-silje-feiring-pasta-bolognese/",
    "Laks og grønnsaker i ovn": "https://oda.com/no/recipes/196-godfisk-no-laks-og-gronnsaker-i-ovn/",
}


async def calculate_weekly_cost():
    """Calculate cost for all recipes."""
    print("\n" + "=" * 80)
    print("💰 Prisberegning - Ukesmeny Uke 1 2026")
    print("=" * 80)
    print(f"\n👨‍👩‍👧‍👦 Familie: 2 voksne + 2 barn (4 porsjoner per rett)")

    total_cost = 0
    all_ingredients = []

    async with OdaRecipeScraper(
        email=settings.oda_email,
        password=settings.oda_password,
        headless=False
    ) as scraper:
        print("\n🔐 Logger inn på Oda.no...")
        await scraper.login()
        print("✅ Innlogget!")

        for i, (recipe_name, recipe_url) in enumerate(RECIPES.items(), 1):
            print(f"\n{'=' * 80}")
            print(f"📋 {i}. {recipe_name}")
            print("=" * 80)

            if not recipe_url:
                print("⚠️  Mangler URL - hopper over")
                continue

            print(f"🔗 {recipe_url}")

            # Navigate to recipe
            await scraper.page.goto(recipe_url, wait_until="networkidle")
            await scraper.page.wait_for_timeout(2000)

            # Try to extract ingredients
            print("\n🥕 Henter ingredienser...")

            # Try different selectors for ingredients
            ingredient_selectors = [
                'li[class*="ingredient"]',
                '[data-testid="ingredient"]',
                'ul.ingredients li',
                '.recipe-ingredients li',
            ]

            ingredients = []
            for selector in ingredient_selectors:
                elements = await scraper.page.query_selector_all(selector)
                if elements:
                    for elem in elements:
                        text = await elem.inner_text()
                        if text and text.strip():
                            ingredients.append(text.strip())
                    break

            if ingredients:
                print(f"✅ Fant {len(ingredients)} ingredienser:")
                for ing in ingredients:
                    print(f"   • {ing}")
                    all_ingredients.append({
                        'recipe': recipe_name,
                        'ingredient': ing
                    })
            else:
                print("⚠️  Kunne ikke hente ingredienser automatisk")
                print("   Viser siden i nettleseren - noter ingredienser manuelt")
                await scraper.page.wait_for_timeout(5000)

        # Now search for prices using Kassal API
        print(f"\n\n{'=' * 80}")
        print("💵 PRISBEREGNING via Kassal.app API")
        print("=" * 80)

        async with KassalClient(api_key=settings.kassal_api_key) as client:
            # Group similar ingredients
            unique_ingredients = {}
            for item in all_ingredients:
                ingredient = item['ingredient']
                # Extract main ingredient (remove amounts)
                # Simple extraction - take first noun-like word
                words = ingredient.lower().split()
                key_ingredient = None

                # Skip numbers and common words
                skip_words = ['stk', 'g', 'kg', 'dl', 'ts', 'ss', 'ca', 'av', 'i', 'eller']
                for word in words:
                    if not any(char.isdigit() for char in word) and word not in skip_words:
                        key_ingredient = word
                        break

                if key_ingredient:
                    if key_ingredient not in unique_ingredients:
                        unique_ingredients[key_ingredient] = {
                            'full_text': ingredient,
                            'recipes': [item['recipe']],
                            'price': None
                        }
                    else:
                        unique_ingredients[key_ingredient]['recipes'].append(item['recipe'])

            print(f"\n📦 Søker priser for {len(unique_ingredients)} unike ingredienser...\n")

            total_estimated = 0
            products_with_price = 0

            for key_ingredient, data in list(unique_ingredients.items())[:15]:  # Limit to first 15
                print(f"🔍 Søker: {key_ingredient} ({data['full_text']})")

                params = ProductSearchParams(search=key_ingredient, size=1)
                try:
                    results = await client.search_products(params)

                    if results.data and results.data[0].current_price:
                        price = results.data[0].current_price
                        product_name = results.data[0].name
                        print(f"   ✅ {product_name}: {price} kr")
                        data['price'] = price
                        total_estimated += price
                        products_with_price += 1
                    else:
                        print(f"   ⚠️  Ingen pris tilgjengelig")
                except Exception as e:
                    print(f"   ❌ Feil: {e}")

                await asyncio.sleep(0.5)  # Rate limiting

            # Summary
            print(f"\n\n{'=' * 80}")
            print("📊 PRISOPPSUMMERING")
            print("=" * 80)
            print(f"\n💰 Estimert totalkostnad: {total_estimated:.2f} kr")
            print(f"📦 Produkter med pris: {products_with_price}/{len(unique_ingredients)}")
            print(f"\n⚠️  MERK: Dette er et ESTIMAT basert på første søkeresultat")
            print(f"   Faktisk pris kan variere avhengig av:")
            print(f"   • Valg av merkevare")
            print(f"   • Pakningsstørrelse")
            print(f"   • Tilbud og kampanjer")
            print(f"   • Ingredienser uten pris i Kassal-databasen")
            print(f"\n💡 Reell pris er trolig: {total_estimated * 1.5:.2f} - {total_estimated * 2.5:.2f} kr")
            print(f"   (inkludert alle ingredienser og missing prices)")

            print(f"\n{'=' * 80}\n")


if __name__ == "__main__":
    asyncio.run(calculate_weekly_cost())
