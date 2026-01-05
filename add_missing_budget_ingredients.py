#!/usr/bin/env python3
"""Add missing ingredients for budget meals to cart."""

import asyncio
from src.config import settings
from src.oda.cart import OdaCartManager


# Missing ingredients with VERY specific search terms to avoid expensive variants
MISSING_INGREDIENTS = [
    ("Hermetiske tomat hakket", 2),  # Canned diced tomatoes - avoid fresh/organic
    ("Kidney bønner hermetikk", 1),  # Kidney beans canned
    ("Jasmin ris billig", 1),  # Cheap jasmine rice
    ("Taco krydder First Price", 1),  # Cheap taco spice
    ("Kraft buljong grønnsak", 2),  # Bouillon cubes
    ("Gulrot pose", 1),  # Bagged carrots (cheaper than loose)
]


async def main():
    """Add missing budget ingredients to cart."""
    print("=" * 80)
    print("🛒 LEGGER TIL MANGLENDE BUDSJETT-INGREDIENSER")
    print("=" * 80)
    print()
    print("Handlekurv nå: ~598 kr")
    print("Skal legge til: ~150 kr")
    print("Mål: ~750 kr for 4 middager")
    print()
    print("=" * 80)
    print()

    async with OdaCartManager(
        settings.oda_email,
        settings.oda_password,
        headless=False
    ) as cart:

        await cart.login()
        print("✅ Innlogget!\n")

        added = 0
        failed = 0

        for product_name, qty in MISSING_INGREDIENTS:
            print(f"Legger til: {product_name} x{qty}... ", end='', flush=True)

            success = await cart.add_product_by_search(product_name, quantity=qty)

            if success:
                print("✅")
                added += 1
            else:
                print("❌ (prøv manuelt)")
                failed += 1

            await asyncio.sleep(2)

        print()
        print("=" * 80)
        print("RESULTAT")
        print("=" * 80)
        print(f"✅ Lagt til: {added}/{len(MISSING_INGREDIENTS)}")
        print(f"❌ Feilet: {failed}/{len(MISSING_INGREDIENTS)}")
        print()

        if failed > 0:
            print("⚠️  Noen produkter feilet - du må legge til disse manuelt:")
            print()
            for i, (product, qty) in enumerate(MISSING_INGREDIENTS, 1):
                print(f"   {i}. {product} x{qty}")
            print()

        print("=" * 80)
        print("NESTE STEG")
        print("=" * 80)
        print()
        print("1. Sjekk handlekurven i nettleseren som er åpen")
        print("2. Verifiser at totalen er rundt ~750 kr")
        print("3. Legg til manglende produkter manuelt hvis noen feilet")
        print("4. Sjekk oppskriftene i:")
        print("   Oppskrifter/Uke 1 - 2026/OPPSKRIFTER - 4 BUDSJETT MIDDAGER - Uke 1.txt")
        print()
        print("💰 MED DISSE 4 MIDDAGENE:")
        print("   - Spaghetti Bolognese")
        print("   - Chili sin carne (vegetar)")
        print("   - Kjøttboller med pasta")
        print("   - Pølse- og potetgryte")
        print()
        print("= 16 porsjoner for ~750 kr = ~47 kr/porsjon ✅✅✅")
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
