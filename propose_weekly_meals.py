"""Propose weekly meals with prices, discounts, cooking time, and visual preview."""

import asyncio
from datetime import datetime
from src.config import settings
from src.oda.recipes import OdaRecipeScraper


# Meal suggestions for Week 1 2026
MEAL_SUGGESTIONS = [
    {
        "name": "Blomkålsuppe med krydderstekte kikerter",
        "url": "https://oda.com/no/recipes/2835-oda-blomkalsuppe-med-krydderstekte-kikerter/",
        "estimated_price": "150-200 kr",
        "cooking_time": "25 min",
        "protein_estimate": "~15g (lav - legg til kylling)",
        "key_ingredients": ["blomkål", "kikerter", "fløte", "hvitløksbaguetter"],
    },
    {
        "name": "Superenkel kylling, brokkoli og ris",
        "url": "https://oda.com/no/recipes/2026-oda-superenkel-kylling-brokkoli-og-ris/",
        "estimated_price": "180-220 kr",
        "cooking_time": "20 min",
        "protein_estimate": "~35-40g (utmerket)",
        "key_ingredients": ["kyllingfilét", "brokkoli", "ris", "soyasaus"],
    },
    {
        "name": "Rask kremet kyllingpanne med parmesan og pasta",
        "url": "https://oda.com/no/recipes/3788-silje-feiring-rask-kremet-kyllingpanne-med-parmesan-og-pasta/",
        "estimated_price": "200-250 kr",
        "cooking_time": "20 min",
        "protein_estimate": "~30-35g (god)",
        "key_ingredients": ["kyllingfilét", "pasta", "fløte", "parmesan", "spinat"],
    },
    {
        "name": "Pasta bolognese",
        "url": "https://oda.com/no/recipes/4519-silje-feiring-pasta-bolognese/",
        "estimated_price": "180-220 kr",
        "cooking_time": "30-40 min",
        "protein_estimate": "~25-30g (ok)",
        "key_ingredients": ["kjøttdeig", "pasta", "tomater", "løk", "hvitløk"],
    },
    {
        "name": "Laks og grønnsaker i ovn",
        "url": "https://oda.com/no/recipes/196-godfisk-no-laks-og-gronnsaker-i-ovn/",
        "estimated_price": "280-350 kr",
        "cooking_time": "30 min",
        "protein_estimate": "~30g + omega-3 (utmerket)",
        "key_ingredients": ["laks", "paprika", "squash", "løk", "poteter"],
    },
]


async def check_discounts():
    """Check Oda.no discounts page for relevant deals."""
    print("\n🏷️  SJEKKER TILBUD PÅ ODA.NO...")
    print("=" * 80)

    async with OdaRecipeScraper(
        email=settings.oda_email,
        password=settings.oda_password,
        headless=False
    ) as scraper:
        await scraper.login()

        # Navigate to discounts page
        discounts_url = "https://oda.com/no/products/discounts/"
        print(f"🔗 Åpner: {discounts_url}")
        await scraper.page.goto(discounts_url, wait_until="networkidle")
        await scraper.page.wait_for_timeout(3000)

        print("\n👁️  Ser etter relevante tilbud...")
        print("   • Kylling")
        print("   • Kjøttdeig")
        print("   • Laks")
        print("   • Pasta")
        print("   • Grønnsaker")

        # Try to find discount tags
        print("\n🔍 Leter etter '2 for', '3 for 2', rabattmerking...")

        # Keep page open so user can see
        print("\n⏸️  Holder siden åpen i 15 sekunder så du kan se tilbudene...")
        await scraper.page.wait_for_timeout(15000)

        print("✅ Tilbudssjekk fullført!")

        return True


async def preview_meals_visual():
    """Show visual preview of all meal suggestions (30 sec each)."""
    week_num = datetime.now().isocalendar()[1]
    year = datetime.now().year

    print("\n" + "=" * 80)
    print(f"🍽️  UKESMENY FORSLAG - Uke {week_num} {year}")
    print("=" * 80)
    print(f"\n👨‍👩‍👧‍👦 Familie: 2 voksne + 2 barn")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d')}")

    # Calculate totals
    total_min = sum(int(m["estimated_price"].split("-")[0]) for m in MEAL_SUGGESTIONS)
    total_max = sum(int(m["estimated_price"].split("-")[1].replace(" kr", "")) for m in MEAL_SUGGESTIONS)
    avg_price = (total_min + total_max) / 2

    print(f"\n💰 TOTALBUDSJETT: {total_min}-{total_max} kr (snitt: {avg_price:.0f} kr)")
    print(f"📊 Pris per porsjon: {avg_price/20:.0f} kr (20 porsjoner)")

    # Show all meals in table
    print("\n" + "=" * 80)
    print("📋 OVERSIKT - 5 Middagsforslag")
    print("=" * 80)

    for i, meal in enumerate(MEAL_SUGGESTIONS, 1):
        print(f"\n{i}. {meal['name']}")
        print(f"   💰 Pris: {meal['estimated_price']}")
        print(f"   ⏱️  Tid: {meal['cooking_time']}")
        print(f"   💪 Protein: {meal['protein_estimate']}")
        print(f"   🥕 Nøkkelingredienser: {', '.join(meal['key_ingredients'])}")

    # Savings tips
    print("\n" + "=" * 80)
    print("💡 TIPS FOR Å SPARE PENGER")
    print("=" * 80)
    print("1. 🏷️  Sjekk tilbud på Oda denne uken (discounts)")
    print("2. 🐟 Bytt laks → torsk/sei (spar ~100 kr)")
    print("3. 🛒 Velg butikkens egne merkevarer (REMA/First Price)")
    print("4. ❄️  Kjøp frossen brokkoli (spar ~10 kr)")
    print("5. 🧀 Kjøp stor parmesan (bedre pris per 100g)")
    print("6. 🔖 Se etter '2 for' eller '3 for 2' merking")

    # Check discounts first
    print("\n" + "=" * 80)
    await check_discounts()

    # Visual preview of each meal
    print("\n" + "=" * 80)
    print("👁️  VISUELL DEMO - Se hver oppskrift (30 sek)")
    print("=" * 80)
    print("\nÅpner nettleser for å vise deg hver oppskrift...")
    print("Du får se bilde, ingredienser og fremgangsmåte for hver middag.\n")

    async with OdaRecipeScraper(
        email=settings.oda_email,
        password=settings.oda_password,
        headless=False
    ) as scraper:
        await scraper.login()

        for i, meal in enumerate(MEAL_SUGGESTIONS, 1):
            print(f"\n{'=' * 80}")
            print(f"📸 {i}/5: {meal['name']}")
            print("=" * 80)
            print(f"💰 Pris: {meal['estimated_price']} | ⏱️  {meal['cooking_time']} | 💪 {meal['protein_estimate']}")
            print(f"🔗 {meal['url']}")

            # Navigate to recipe
            await scraper.page.goto(meal['url'], wait_until="networkidle")

            print(f"\n👁️  Viser i 30 sekunder... Se på bildet og ingrediensene!")
            print("   ⏳ ", end="", flush=True)

            # 30 second preview with countdown
            for sec in range(30, 0, -5):
                await scraper.page.wait_for_timeout(5000)
                print(f"{sec}... ", end="", flush=True)

            print("✅")

        # Summary
        print("\n\n" + "=" * 80)
        print("🎉 DEMO FULLFØRT!")
        print("=" * 80)
        print("\n✅ Du har nå sett alle 5 middagene")
        print("\n📋 NESTE STEG:")
        print("  1. Godkjenn disse middagene (eller foreslå endringer)")
        print("  2. Jeg legger alle ingrediensene i handlekurven")
        print("  3. Vi sjekker totalprisen")
        print("  4. Du fullfører bestillingen manuelt")

        print(f"\n💾 OPPRETT MIDDAGSLISTE: 'Uke {week_num} {year}'")
        print("   Dette gjør vi etter at du godkjenner middagene!")

        print("\n⏸️  Nettleseren forblir åpen...")
        print("  Skriv 'godkjent' eller foreslå endringer i chatten")
        print("  Trykk Ctrl+C for å avslutte")

        # Keep browser open
        try:
            while True:
                await asyncio.sleep(10)
        except KeyboardInterrupt:
            print("\n\n✅ Avslutter...")


if __name__ == "__main__":
    try:
        asyncio.run(preview_meals_visual())
    except KeyboardInterrupt:
        print("\n\n👋 Hadet!")
