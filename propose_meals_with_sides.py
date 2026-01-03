"""Propose weekly meals with prices, sides, and automatic cookie dismissal."""

import asyncio
from datetime import datetime
from src.config import settings
from src.oda.recipes import OdaRecipeScraper


# Meal suggestions with recommended sides
MEAL_SUGGESTIONS = [
    {
        "name": "Blomkålsuppe med krydderstekte kikerter",
        "url": "https://oda.com/no/recipes/2835-oda-blomkalsuppe-med-krydderstekte-kikerter/",
        "estimated_price": "150-200 kr",
        "cooking_time": "25 min",
        "protein_estimate": "~15g (lav - legg til kylling)",
        "key_ingredients": ["blomkål", "kikerter", "fløte", "hvitløksbaguetter"],
        "recommended_sides": [
            {"item": "Hvitløksbaguetter", "price": "30-40 kr", "why": "Perfekt til å dyppe i suppen"},
            {"item": "Grønn salat", "price": "25-35 kr", "why": "Gir friskhet til den kremete suppen"},
            {"item": "Revet ost (topping)", "price": "30 kr", "why": "Ekstra smak og protein"},
        ]
    },
    {
        "name": "Superenkel kylling, brokkoli og ris",
        "url": "https://oda.com/no/recipes/2026-oda-superenkel-kylling-brokkoli-og-ris/",
        "estimated_price": "180-220 kr",
        "cooking_time": "20 min",
        "protein_estimate": "~35-40g (utmerket)",
        "key_ingredients": ["kyllingfilét", "brokkoli", "ris", "soyasaus"],
        "recommended_sides": [
            {"item": "Agurksalat (asiatisk)", "price": "20-30 kr", "why": "Frisk og sprø kontrast"},
            {"item": "Sesamfrø (topping)", "price": "25 kr", "why": "Autentisk asiatisk smak"},
            {"item": "Sweet chili saus", "price": "30 kr", "why": "Ekstra smak for barna"},
        ]
    },
    {
        "name": "Rask kremet kyllingpanne med parmesan og pasta",
        "url": "https://oda.com/no/recipes/3788-silje-feiring-rask-kremet-kyllingpanne-med-parmesan-og-pasta/",
        "estimated_price": "200-250 kr",
        "cooking_time": "20 min",
        "protein_estimate": "~30-35g (god)",
        "key_ingredients": ["kyllingfilét", "pasta", "fløte", "parmesan", "spinat"],
        "recommended_sides": [
            {"item": "Grønn salat med balsamico", "price": "30-40 kr", "why": "Klassisk til pasta"},
            {"item": "Hvitløksbrød", "price": "30 kr", "why": "Barn elsker det!"},
            {"item": "Cherry tomater", "price": "35 kr", "why": "Farge og friskhet"},
        ]
    },
    {
        "name": "Pasta bolognese",
        "url": "https://oda.com/no/recipes/4519-silje-feiring-pasta-bolognese/",
        "estimated_price": "180-220 kr",
        "cooking_time": "30-40 min",
        "protein_estimate": "~25-30g (ok)",
        "key_ingredients": ["kjøttdeig", "pasta", "tomater", "løk", "hvitløk"],
        "recommended_sides": [
            {"item": "Grønn salat", "price": "25-35 kr", "why": "Balanserer den tunge sausen"},
            {"item": "Revet parmesan", "price": "40 kr", "why": "Klassisk topping"},
            {"item": "Focaccia brød", "price": "35 kr", "why": "Italiensk autentisk"},
        ]
    },
    {
        "name": "Laks og grønnsaker i ovn",
        "url": "https://oda.com/no/recipes/196-godfisk-no-laks-og-gronnsaker-i-ovn/",
        "estimated_price": "280-350 kr",
        "cooking_time": "30 min",
        "protein_estimate": "~30g + omega-3 (utmerket)",
        "key_ingredients": ["laks", "paprika", "squash", "løk", "poteter"],
        "recommended_sides": [
            {"item": "Sitron (kvarter)", "price": "15-20 kr", "why": "Perfekt til fisk"},
            {"item": "Rømme/tzatziki", "price": "30 kr", "why": "Kremet dip til laksen"},
            {"item": "Fersk dill", "price": "25 kr", "why": "Klassisk til laks"},
        ]
    },
]


async def hide_cookie_popup(page):
    """Automatically hide cookie consent popups."""
    try:
        # Common cookie popup selectors
        cookie_selectors = [
            'button:has-text("Godta alle")',
            'button:has-text("Godta")',
            'button:has-text("Accept")',
            'button:has-text("Aksepter")',
            '[id*="cookie"] button',
            '[class*="cookie"] button',
            '.cookie-consent button',
            '#CybotCookiebotDialogBodyButtonAccept',
            '#onetrust-accept-btn-handler',
        ]

        for selector in cookie_selectors:
            try:
                button = await page.query_selector(selector)
                if button:
                    await button.click()
                    print("   ✅ Cookie popup skjult")
                    return True
            except Exception:
                continue

        # Try to hide cookie banner with CSS if button not found
        await page.add_style_tag(content="""
            [id*="cookie"],
            [class*="cookie"],
            [id*="consent"],
            [class*="consent"],
            .cookie-banner,
            .cookie-notice {
                display: none !important;
            }
        """)

        return True
    except Exception as e:
        print(f"   ⚠️  Kunne ikke skjule cookie popup: {e}")
        return False


async def propose_meals_with_sides():
    """Propose meals with automatic sides suggestions."""
    week_num = datetime.now().isocalendar()[1]
    year = datetime.now().year

    print("\n" + "=" * 80)
    print(f"🍽️  UKESMENY FORSLAG - Uke {week_num} {year}")
    print("=" * 80)
    print(f"\n👨‍👩‍👧‍👦 Familie: 2 voksne + 2 barn")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d')}")

    # Calculate totals for main meals
    total_meals_min = sum(int(m["estimated_price"].split("-")[0]) for m in MEAL_SUGGESTIONS)
    total_meals_max = sum(int(m["estimated_price"].split("-")[1].replace(" kr", "")) for m in MEAL_SUGGESTIONS)
    avg_meals = (total_meals_min + total_meals_max) / 2

    # Calculate sides totals (if taking recommended sides)
    total_sides_min = 0
    total_sides_max = 0
    for meal in MEAL_SUGGESTIONS:
        for side in meal["recommended_sides"]:
            price_range = side["price"].replace(" kr", "").split("-")
            if len(price_range) == 2:
                total_sides_min += int(price_range[0])
                total_sides_max += int(price_range[1])
            else:
                total_sides_min += int(price_range[0])
                total_sides_max += int(price_range[0])

    avg_sides = (total_sides_min + total_sides_max) / 2

    print(f"\n💰 HOVEDRETTER: {total_meals_min}-{total_meals_max} kr (snitt: {avg_meals:.0f} kr)")
    print(f"🥗 TILBEHØR (hvis alt inkluderes): {total_sides_min}-{total_sides_max} kr (snitt: {avg_sides:.0f} kr)")
    print(f"📊 TOTALT MED ALT TILBEHØR: {total_meals_min + total_sides_min}-{total_meals_max + total_sides_max} kr")

    # Show overview
    print("\n" + "=" * 80)
    print("📋 OVERSIKT - 5 Middagsforslag med Tilbehør")
    print("=" * 80)

    for i, meal in enumerate(MEAL_SUGGESTIONS, 1):
        print(f"\n{i}. {meal['name']}")
        print(f"   💰 Hovedrett: {meal['estimated_price']}")
        print(f"   ⏱️  Tid: {meal['cooking_time']}")
        print(f"   💪 Protein: {meal['protein_estimate']}")

        print(f"\n   🍴 FORESLÅTTE TILBEHØR:")
        for side in meal["recommended_sides"]:
            print(f"      • {side['item']} ({side['price']}) - {side['why']}")

    # Savings tips
    print("\n" + "=" * 80)
    print("💡 TIPS FOR Å SPARE PENGER")
    print("=" * 80)
    print("1. 🏷️  Sjekk tilbud på Oda denne uken (discounts)")
    print("2. 🐟 Bytt laks → torsk/sei (spar ~100 kr)")
    print("3. 🛒 Velg butikkens egne merkevarer (REMA/First Price)")
    print("4. 🥗 Hopp over noen tilbehør (spar ~400 kr)")
    print("5. 🧀 Kjøp stor parmesan (bedre pris per 100g)")
    print("6. 🔖 Se etter '2 for' eller '3 for 2' merking")

    # Visual preview
    print("\n" + "=" * 80)
    print("👁️  VISUELL DEMO - Se hver oppskrift (30 sek)")
    print("=" * 80)
    print("\nÅpner nettleser for å vise deg hver oppskrift...")
    print("Cookie popups blir automatisk skjult! 🍪❌\n")

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
            print(f"💰 {meal['estimated_price']} | ⏱️  {meal['cooking_time']} | 💪 {meal['protein_estimate']}")
            print(f"🔗 {meal['url']}")

            # Navigate to recipe
            await scraper.page.goto(meal['url'], wait_until="networkidle")

            # Hide cookie popup
            await hide_cookie_popup(scraper.page)
            await scraper.page.wait_for_timeout(1000)

            print(f"\n👁️  Viser i 30 sekunder... Se på bildet og ingrediensene!")

            # Show recommended sides while viewing
            print(f"\n   🍴 Tilbehør til denne:")
            for side in meal["recommended_sides"]:
                print(f"      • {side['item']} - {side['why']}")

            print("\n   ⏳ ", end="", flush=True)

            # 30 second preview
            for sec in range(30, 0, -5):
                await scraper.page.wait_for_timeout(5000)
                print(f"{sec}... ", end="", flush=True)

            print("✅")

        # Summary and questions
        print("\n\n" + "=" * 80)
        print("🎉 DEMO FULLFØRT!")
        print("=" * 80)

        print("\n✅ Du har sett alle 5 middagene med tilbehørsforslag")

        print("\n" + "=" * 80)
        print("❓ OPPFØLGINGSSPØRSMÅL")
        print("=" * 80)

        print("\n1️⃣  Godkjenner du disse 5 hovedrettene?")
        print("   → Skriv 'godkjent' eller foreslå endringer")

        print("\n2️⃣  Hvilke TILBEHØR vil du ha?")
        print("   → Alle foreslåtte tilbehør? (+{:.0f} kr)".format(avg_sides))
        print("   → Bare salat og brød? (~150 kr)")
        print("   → Ingen tilbehør? (0 kr)")
        print("   → Velg selv? (spesifiser hvilke)")

        print("\n3️⃣  Trenger du noe EKSTRA?")
        print("   → Drikkevarer (juice, brus, vann)?")
        print("   → Snacks til barna?")
        print("   → Frukt?")
        print("   → Yoghurt/dessert?")

        print(f"\n💾 Etter godkjenning oppretter jeg 'Middagsliste: Uke {week_num} {year}'")

        print("\n⏸️  Nettleseren forblir åpen...")
        print("  Svar på spørsmålene i chatten, så går vi videre!")
        print("  Trykk Ctrl+C for å avslutte")

        # Keep browser open
        try:
            while True:
                await asyncio.sleep(10)
        except KeyboardInterrupt:
            print("\n\n✅ Avslutter...")


if __name__ == "__main__":
    try:
        asyncio.run(propose_meals_with_sides())
    except KeyboardInterrupt:
        print("\n\n👋 Hadet!")
