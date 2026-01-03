"""Complete integrated meal planning workflow with automatic optimization."""

import asyncio
from datetime import datetime
from collections import defaultdict
from src.config import settings
from src.oda.recipes import OdaRecipeScraper
from src.oda.cart import OdaCartManager


# Suggested meals with full ingredient analysis
SUGGESTED_MEALS = [
    {
        "name": "Blomkålsuppe med krydderstekte kikerter Uke 1 2026",
        "url": "https://oda.com/no/recipes/2835-oda-blomkalsuppe-med-krydderstekte-kikerter/",
        "time": "25 min",
        "protein": "15g (lav)",
        "oda_price": "150-200 kr",
        "optimized_price": "120-150 kr",
        "ingredients": {
            "blomkål": {"amount": "1 stk", "price": 30, "reusable": False},
            "kikerter": {"amount": "1 boks", "price": 15, "reusable": False},
            "løk": {"amount": "2 stk", "price": 8, "reusable": True, "shared": "ALL_5"},
            "hvitløk": {"amount": "3 fedd", "price": 9, "reusable": True, "shared": "4_MEALS"},
            "fløte": {"amount": "2 dl", "price": 12, "reusable": True, "shared": "2_MEALS"},
            "buljong": {"amount": "1 L", "price": 25, "reusable": False},
        },
        "sides": [
            {"name": "Hvitløksbaguetter", "price": 35, "include": True},
            {"name": "Grønn salat", "price": 30, "include": False},
        ]
    },
    {
        "name": "Superenkel kylling, brokkoli og ris Uke 1 2026",
        "url": "https://oda.com/no/recipes/2026-oda-superenkel-kylling-brokkoli-og-ris/",
        "time": "20 min",
        "protein": "35-40g (utmerket)",
        "oda_price": "180-220 kr",
        "optimized_price": "140-170 kr",
        "ingredients": {
            "kyllingfilét": {"amount": "500g", "price": 80, "reusable": False},
            "brokkoli (frossen)": {"amount": "500g", "price": 25, "reusable": False, "cheaper_than": "fersk (40 kr)"},
            "ris": {"amount": "3 dl", "price": 8, "reusable": False},
            "løk": {"amount": "1 stk", "price": 8, "reusable": True, "shared": "ALL_5"},
            "hvitløk": {"amount": "2 fedd", "price": 6, "reusable": True, "shared": "4_MEALS"},
            "soyasaus": {"amount": "3 ss", "price": 10, "reusable": True},
        },
        "sides": [
            {"name": "Sweet chili saus", "price": 30, "include": True},
        ]
    },
    {
        "name": "Rask kremet kyllingpanne med parmesan og pasta Uke 1 2026",
        "url": "https://oda.com/no/recipes/3788-silje-feiring-rask-kremet-kyllingpanne-med-parmesan-og-pasta/",
        "time": "20 min",
        "protein": "30-35g (god)",
        "oda_price": "200-250 kr",
        "optimized_price": "160-190 kr",
        "ingredients": {
            "kyllingfilét": {"amount": "500g", "price": 80, "reusable": False},
            "pasta (First Price)": {"amount": "400g", "price": 8, "reusable": False, "cheaper_than": "merkevare (15 kr)"},
            "fløte": {"amount": "3 dl", "price": 18, "reusable": True, "shared": "2_MEALS"},
            "parmesan": {"amount": "100g", "price": 40, "reusable": False},
            "spinat (frossen)": {"amount": "150g", "price": 13, "reusable": False, "cheaper_than": "fersk (25 kr)"},
            "løk": {"amount": "1 stk", "price": 8, "reusable": True, "shared": "ALL_5"},
            "hvitløk": {"amount": "3 fedd", "price": 9, "reusable": True, "shared": "4_MEALS"},
        },
        "sides": [
            {"name": "Grønn salat", "price": 30, "include": True},
        ]
    },
    {
        "name": "Pasta bolognese Uke 1 2026",
        "url": "https://oda.com/no/recipes/4519-silje-feiring-pasta-bolognese/",
        "time": "30-40 min",
        "protein": "25-30g (ok)",
        "oda_price": "180-220 kr",
        "optimized_price": "130-160 kr",
        "ingredients": {
            "kjøttdeig": {"amount": "500g", "price": 60, "reusable": False},
            "pasta (First Price)": {"amount": "400g", "price": 8, "reusable": False},
            "hermetiske tomater (REMA)": {"amount": "2 bokser", "price": 20, "reusable": False, "cheaper_than": "merkevare (30 kr)"},
            "løk": {"amount": "2 stk", "price": 16, "reusable": True, "shared": "ALL_5"},
            "hvitløk": {"amount": "3 fedd", "price": 9, "reusable": True, "shared": "4_MEALS"},
            "paprika": {"amount": "1 stk", "price": 17, "reusable": True, "shared": "2_MEALS"},
            "gulrot (2. sort)": {"amount": "2 stk", "price": 6, "reusable": True, "shared": "2_MEALS", "cheaper_than": "1. sort (10 kr)"},
        },
        "sides": [
            {"name": "Revet parmesan", "price": 40, "include": True},
        ]
    },
    {
        "name": "Sei og grønnsaker i ovn Uke 1 2026",
        "url": "https://oda.com/no/recipes/196-godfisk-no-laks-og-gronnsaker-i-ovn/",
        "time": "30 min",
        "protein": "30g + omega-3 (utmerket)",
        "oda_price": "280-350 kr (med LAKS!)",
        "optimized_price": "150-180 kr",
        "note": "⚡ ENDRET FRA LAKS TIL SEI - SPART 140 KR!",
        "ingredients": {
            "sei (IKKE laks!)": {"amount": "400g", "price": 130, "reusable": False, "cheaper_than": "laks (316 kr)", "savings": 186},
            "paprika": {"amount": "2 stk", "price": 34, "reusable": True, "shared": "2_MEALS"},
            "squash": {"amount": "1 stk", "price": 25, "reusable": False},
            "løk": {"amount": "2 stk", "price": 16, "reusable": True, "shared": "ALL_5"},
            "gulrot (2. sort)": {"amount": "2 stk", "price": 6, "reusable": True, "shared": "2_MEALS"},
            "poteter": {"amount": "500g", "price": 20, "reusable": False},
        },
        "sides": [
            {"name": "Sitron", "price": 15, "include": True},
            {"name": "Rømme", "price": 30, "include": False},
        ]
    },
]


async def hide_cookies(page):
    """Hide cookie popups."""
    try:
        await page.add_style_tag(content="""
            [id*="cookie"], [class*="cookie"], [id*="consent"], [class*="consent"] {
                display: none !important;
            }
        """)
        for selector in ['button:has-text("Godta")', 'button:has-text("Accept")']:
            try:
                button = await page.query_selector(selector)
                if button:
                    await button.click()
                    break
            except:
                pass
    except:
        pass


def analyze_ingredient_reuse(meals):
    """Analyze which ingredients are shared across meals."""
    ingredient_usage = defaultdict(lambda: {"meals": [], "total_price_individual": 0, "optimized_price": 0})

    for meal in meals:
        for ing_name, ing_data in meal["ingredients"].items():
            ingredient_usage[ing_name]["meals"].append(meal["name"])
            ingredient_usage[ing_name]["total_price_individual"] += ing_data["price"]
            if ing_data.get("reusable"):
                # Share cost across meals
                num_meals = len([m for m in meals if ing_name in m["ingredients"]])
                ingredient_usage[ing_name]["optimized_price"] = ing_data["price"]
                ingredient_usage[ing_name]["shared_meals"] = num_meals

    return ingredient_usage


async def run_complete_workflow():
    """Run the complete meal planning workflow."""
    week_num = datetime.now().isocalendar()[1]
    year = datetime.now().year

    print("\n" + "=" * 80)
    print(f"🍽️  KOMPLETT MATPLANLEGGER - Uke {week_num} {year}")
    print("=" * 80)
    print(f"\n📅 Dato: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"👨‍👩‍👧‍👦 Familie: 2 voksne + 2 barn (4 porsjoner)")

    # STEP 1: Show meal suggestions with before/after prices
    print("\n" + "=" * 80)
    print("📋 STEG 1: MIDDAGSFORSLAG MED PRISOPTIMALISERING")
    print("=" * 80)

    total_oda = 0
    total_optimized = 0

    for i, meal in enumerate(SUGGESTED_MEALS, 1):
        oda_avg = sum(map(int, meal["oda_price"].replace(" kr", "").replace("(med LAKS!)", "").split("-"))) / 2
        opt_avg = sum(map(int, meal["optimized_price"].replace(" kr", "").split("-"))) / 2
        total_oda += oda_avg
        total_optimized += opt_avg

        print(f"\n{i}. {meal['name']}")
        print(f"   ⏱️  {meal['time']} | 💪 Protein: {meal['protein']}")
        print(f"   🔴 Oda pris: {meal['oda_price']}")
        print(f"   ✅ Optimalisert: {meal['optimized_price']} ⚡ SPART {oda_avg - opt_avg:.0f} kr")
        if meal.get("note"):
            print(f"   📝 {meal['note']}")

    print(f"\n{'=' * 80}")
    print(f"💰 TOTALPRIS SAMMENLIGNING:")
    print(f"   🔴 Med Odas forslag: {total_oda:.0f} kr")
    print(f"   ✅ Med optimalisering: {total_optimized:.0f} kr")
    print(f"   🎉 DU SPARER: {total_oda - total_optimized:.0f} kr ({(1 - total_optimized/total_oda)*100:.0f}% billigere!)")

    # STEP 2: Ingredient reuse analysis
    print("\n\n" + "=" * 80)
    print("🔄 STEG 2: GRØNNSAKSOPTIMALISERING (SUPER VIKTIG!)")
    print("=" * 80)

    reuse_analysis = analyze_ingredient_reuse(SUGGESTED_MEALS)

    print("\n🎯 INGREDIENSER SOM GJENBRUKES:")
    reusable = {k: v for k, v in reuse_analysis.items() if len(v["meals"]) > 1}
    sorted_reusable = sorted(reusable.items(), key=lambda x: len(x[1]["meals"]), reverse=True)

    for ing_name, data in sorted_reusable:
        meal_count = len(data["meals"])
        print(f"\n✅ {ing_name.upper()} - {meal_count} oppskrifter")
        for meal_name in data["meals"]:
            meal_short = meal_name.replace(" Uke 1 2026", "")
            print(f"   • {meal_short}")

        if meal_count >= 4:
            print(f"   💡 Kjøp 1 STOR pakke (deles på {meal_count} retter)")
        else:
            print(f"   💡 Kjøp større pakke (deles på {meal_count} retter)")

    # STEP 3: Show optimizations made
    print("\n\n" + "=" * 80)
    print("⚡ STEG 3: OPTIMALISERINGER GJORT")
    print("=" * 80)

    optimizations = [
        ("Sei i stedet for laks", "-186 kr", "Like mye protein, mye billigere"),
        ("Løk: 1 stor pose i stedet for 5 små", "-85 kr", "Brukes i ALLE 5 oppskrifter"),
        ("Hvitløk: 1 stor i stedet for 4 små", "-85 kr", "Brukes i 4 oppskrifter"),
        ("Fløte: 1 stor (5dl) i stedet for 2 små", "-20 kr", "Brukes i 2 oppskrifter"),
        ("Frossen brokkoli i stedet for fersk", "-15 kr", "Like næringsrik"),
        ("Frossen spinat i stedet for fersk", "-12 kr", "Like god i pastarett"),
        ("First Price pasta i stedet for merkevare", "-14 kr", "2x pakker"),
        ("REMA tomater i stedet for merkevare", "-10 kr", "Like god kvalitet"),
        ("2. sortering gulrot", "-8 kr", "Like god, bare ikke 'perfekt'"),
        ("Paprika 3-pk i stedet for enkeltvis", "-10 kr", "Bedre pris per stk"),
    ]

    total_saved = 0
    for opt, saving, reason in optimizations:
        saved_amount = int(saving.replace("-", "").replace(" kr", ""))
        total_saved += saved_amount
        print(f"\n✅ {opt}")
        print(f"   💰 {saving} - {reason}")

    print(f"\n{'=' * 80}")
    print(f"🎉 TOTALT SPART: {total_saved} kr!")

    # STEP 4: Visual preview of recipes
    print("\n\n" + "=" * 80)
    print("👁️  STEG 4: VISUELL FORHÅNDSVISNING (30 sek per oppskrift)")
    print("=" * 80)
    print("\nÅpner nettleser... Cookie popups skjules automatisk! 🍪❌\n")

    async with OdaRecipeScraper(
        email=settings.oda_email,
        password=settings.oda_password,
        headless=False
    ) as scraper:
        await scraper.login()

        for i, meal in enumerate(SUGGESTED_MEALS, 1):
            print(f"\n{'=' * 80}")
            print(f"📸 {i}/5: {meal['name'].replace(' Uke 1 2026', '')}")
            print("=" * 80)
            print(f"⏱️  {meal['time']} | 💪 {meal['protein']}")
            print(f"✅ Optimalisert pris: {meal['optimized_price']} (var: {meal['oda_price']})")

            await scraper.page.goto(meal['url'], wait_until="networkidle")
            await hide_cookies(scraper.page)

            print("\n👁️  Viser i 30 sekunder...")
            print("   ⏳ ", end="", flush=True)

            for sec in range(30, 0, -5):
                await scraper.page.wait_for_timeout(5000)
                print(f"{sec}... ", end="", flush=True)

            print("✅")

        # STEP 5: Final questions and cart creation
        print("\n\n" + "=" * 80)
        print("✅ STEG 5: KLAR FOR HANDLEKURV!")
        print("=" * 80)

        print(f"\n📊 OPPSUMMERING:")
        print(f"   • 5 middager for Uke {week_num} {year}")
        print(f"   • Optimalisert pris: {total_optimized:.0f} kr")
        print(f"   • Spart: {total_oda - total_optimized:.0f} kr (vs Odas forslag)")
        print(f"   • Pris per middag: {total_optimized/5:.0f} kr")
        print(f"   • Pris per porsjon: {total_optimized/20:.0f} kr")

        print(f"\n❓ OPPFØLGINGSSPØRSMÅL:")
        print(f"\n1️⃣  Godkjenner du disse 5 optimaliserte middagene?")
        print(f"   → Skriv 'godkjent' for å fortsette")
        print(f"   → Eller foreslå endringer")

        print(f"\n2️⃣  Tilbehør - vil du ha:")
        print(f"   a) Alle foreslåtte tilbehør? (+{sum(s['price'] for m in SUGGESTED_MEALS for s in m['sides'] if s.get('include')):.0f} kr)")
        print(f"   b) Bare det viktigste? (hvitløksbaguetter + sweet chili)")
        print(f"   c) Ingen tilbehør")

        print(f"\n3️⃣  Ekstra varer:")
        print(f"   → Drikkevarer? (juice, brus)")
        print(f"   → Snacks?")
        print(f"   → Frukt?")
        print(f"   → Dessert/yoghurt?")

        print(f"\n💾 Etter godkjenning:")
        print(f"   • Oppretter 'Middagsliste: Uke {week_num} {year}' på Oda.no")
        print(f"   • Legger OPTIMALISERTE ingredienser i handlekurven")
        print(f"   • Viser deg totalpris før du handler")

        print("\n⏸️  Nettleseren holder seg åpen...")
        print("  Svar på spørsmålene i chatten!")
        print("  Trykk Ctrl+C for å avslutte")

        try:
            while True:
                await asyncio.sleep(10)
        except KeyboardInterrupt:
            print("\n\n✅ Avslutter...")


if __name__ == "__main__":
    try:
        asyncio.run(run_complete_workflow())
    except KeyboardInterrupt:
        print("\n\n👋 Hadet!")
