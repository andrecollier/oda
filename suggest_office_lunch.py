"""Smart lunsjforslag for kontoret - sunt, godt og lett."""

import asyncio
from src.config import settings
from src.kassal.client import KassalClient
from src.kassal.models import ProductSearchParams


LUNCH_IDEAS = [
    {
        "name": "🥗 Proteinrik salat med kylling",
        "portions": 2,
        "prep_time": "15 min",
        "ingredients": [
            "Ferdigstekt kylling (250g)",
            "Salat mix (pose)",
            "Cherrytomater",
            "Agurk",
            "Fetaost",
            "Olivenolje & balsamico"
        ],
        "why": "Lett, mettende, full av protein. Kan forberede kvelden før.",
        "estimated_price": "80-100 kr for 2"
    },
    {
        "name": "🌯 Wraps med hummus og grønnsaker",
        "portions": 2,
        "prep_time": "10 min",
        "ingredients": [
            "Tortilla wraps (4 stk)",
            "Hummus (boks)",
            "Ruccolasalat",
            "Paprika (ferdig kuttet)",
            "Gulrot (stripet)",
            "Reker eller kylling (valgfritt)"
        ],
        "why": "Super enkelt, kan lage om morgenen. Variert og fresh.",
        "estimated_price": "60-80 kr for 2"
    },
    {
        "name": "🍲 Suppe med knekkebrød",
        "portions": 2,
        "prep_time": "5 min oppvarming",
        "ingredients": [
            "Ferdig suppe (pose/kartong) - tomato, grønnsak eller kylling",
            "Knekkebrød",
            "Cottage cheese eller ost",
            "Evt. kokt egg"
        ],
        "why": "Varmende, mettende, minimalt stress. Perfekt for kalde dager.",
        "estimated_price": "50-70 kr for 2"
    },
    {
        "name": "🥙 Lunchbowl med quinoa",
        "portions": 2,
        "prep_time": "20 min (kan forberede)",
        "ingredients": [
            "Quinoa eller bulgur (tørrvar)",
            "Bønner/kikerter (hermetisk)",
            "Grønnsaker (brokkoli, paprika, avokado)",
            "Evt. laks eller egg",
            "Dressing (soyasaus/sitron/olje)"
        ],
        "why": "Sunn, mettende, god energi hele dagen. Meal prep-vennlig.",
        "estimated_price": "70-90 kr for 2"
    },
    {
        "name": "🥪 Gourmet smørbrød",
        "portions": 2,
        "prep_time": "10 min",
        "ingredients": [
            "Grovt brød (helst rugbrød)",
            "Røkelaks ELLER røkt kalkun",
            "Cottage cheese/kremost",
            "Agurk, tomat, salat",
            "Evt. kokt egg"
        ],
        "why": "Klassisk, tilfredsstillende, god variasjon. Norsk tradisjon!",
        "estimated_price": "70-90 kr for 2"
    }
]


async def search_lunch_products():
    """Search for lunch products with prices."""
    print("\n" + "=" * 80)
    print("🛒 PRODUKTSØK MED PRISER")
    print("=" * 80)

    async with KassalClient(api_key=settings.kassal_api_key) as client:
        searches = [
            ("ferdigstekt kylling", "🍗 Ferdigstekt kylling"),
            ("salatmix fersk", "🥬 Salatmix"),
            ("hummus", "🫘 Hummus"),
            ("tortilla wrap", "🌯 Wraps"),
            ("ferdig suppe", "🍲 Ferdigsupper"),
            ("quinoa", "🌾 Quinoa"),
            ("røkelaks", "🐟 Røkelaks"),
        ]

        for search_term, label in searches:
            print(f"\n{label}:")
            params = ProductSearchParams(search=search_term, size=3)
            results = await client.search_products(params)

            if results.data:
                for product in results.data[:3]:
                    price = f"{product.current_price:.2f} kr" if product.current_price else "Pris mangler"
                    store = product.store.name if product.store else "Ukjent butikk"
                    print(f"   • {product.name} ({store}): {price}")
            else:
                print("   Ingen resultater funnet")

            await asyncio.sleep(1.1)  # Rate limiting (60 req/min = 1 req/sec)


async def main():
    print("\n" + "=" * 80)
    print("🥗 LUNSJFORSLAG FOR KONTORET - 2 personer, 2-3 dager/uke")
    print("=" * 80)
    print("\n✅ SUNT • GODT • LETT • ENKELT Å FORBEREDE")

    print("\n" + "=" * 80)
    print("💡 5 ANBEFALTE LUNSJRETTER")
    print("=" * 80)

    for i, lunch in enumerate(LUNCH_IDEAS, 1):
        print(f"\n{i}. {lunch['name']}")
        print(f"   👥 {lunch['portions']} porsjoner | ⏱️  {lunch['prep_time']}")
        print(f"   💰 {lunch['estimated_price']}")
        print(f"   💡 {lunch['why']}")
        print(f"\n   📝 Ingredienser:")
        for ingredient in lunch['ingredients']:
            print(f"      • {ingredient}")

    # Show weekly plan suggestion
    print("\n\n" + "=" * 80)
    print("📅 EKSEMPEL UKEPLAN (2-3 luncher/uke)")
    print("=" * 80)

    print("\n🗓️  MANDAG:")
    print("   → Proteinrik salat med kylling (friskt etter helgen!)")

    print("\n🗓️  ONSDAG:")
    print("   → Wraps med hummus og grønnsaker (raskt og enkelt)")

    print("\n🗓️  FREDAG:")
    print("   → Lunchbowl med quinoa (god energi før helgen)")

    print("\n\n" + "=" * 80)
    print("🎯 TIPS FOR SUKSESS")
    print("=" * 80)
    print("""
1. ✅ Forbered kvelden før (kutt grønnsaker, kok quinoa/egg)
2. ✅ Bruk ferdige produkter når det passer (stekt kylling, hummus, suppe)
3. ✅ Ha alltid salat mix, wraps og knekkebrød på lager
4. ✅ Variere mellom kaldt og varmt (suppe på kalde dager)
5. ✅ Kjøp kvalitetsprodukter - når det er 2 personer blir det rimelig!
6. ✅ Unngå tungt brød og mye karbohydrater midt på dagen
7. ✅ Ha alltid egg og cottage cheese tilgjengelig (backup protein)
""")

    # Search for products with prices
    await search_lunch_products()

    print("\n\n" + "=" * 80)
    print("💰 UKESBUDSJETT FOR 2-3 LUNCHER")
    print("=" * 80)
    print("""
🔴 Restaurant/kantine (2 pers x 3 dager):
   → 150-200 kr per person per gang = 900-1200 kr/uke

✅ Hjemmelaget lunsj (2 pers x 3 dager):
   → 60-90 kr totalt per gang = 180-270 kr/uke

🎉 SPART: 650-900 kr per uke! (3.500-4.500 kr per måned!)
""")

    print("\n" + "=" * 80)
    print("🛒 HANDLELISTE FOR 1 UKE (3 luncher)")
    print("=" * 80)
    print("""
📦 PROTEIN:
   • Ferdigstekt kylling (400g)
   • Reker eller røkelaks (200g)
   • Egg (6 stk)
   • Cottage cheese/kremost

🥬 GRØNNSAKER:
   • Salatmix (pose)
   • Cherrytomater
   • Agurk
   • Paprika (ferdig kuttet)
   • Avokado

🌾 BASISVARER:
   • Tortilla wraps (pakke)
   • Quinoa eller bulgur (pose)
   • Knekkebrød
   • Hummus (boks)
   • Ferdig suppe (1-2 poser)

💡 TOTALT: ~250-350 kr for 3 luncher (2 personer)
   = 40-60 kr per person per lunsj!
""")


if __name__ == "__main__":
    asyncio.run(main())
