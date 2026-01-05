#!/usr/bin/env python3
"""Final cleanup - remove ALL wrong products and add correct ones."""

import asyncio
from src.config import settings
from src.oda.cart import OdaCartManager


# Remove these wrong products
REMOVE_ALL_WRONG = [
    "knekkebrød",
    "runde tomater",
    "sorte bønner",
    "økologisk",  # All økologisk products
    "bacon i terninger",
    "utsolgt",  # All out of stock
]


# Add these with VERY specific searches
CORRECT_PRODUCTS = [
    ("Gulrot pose Norge", 1),  # Try "pose" to get bagged
    ("Hermetiske hakkede tomater", 2),  # "hermetiske" = canned
    ("Kidney rød bønner", 1),  # Red kidney beans
    ("Taco krydder billig", 1),  # Cheap taco spice
    ("Jasmin ris", 1),  # Jasmine rice (usually cheap)
    ("Kraft terning grønnsak", 1),  # Bouillon cubes
]


async def main():
    """Final cleanup."""
    print("="*80)
    print("🧹 ENDELIG OPPRYDDING")
    print("="*80)
    print()

    async with OdaCartManager(
        settings.oda_email,
        settings.oda_password,
        headless=False
    ) as cart:

        await cart.login()
        print("✅ Innlogget!\n")

        # STEP 1: Remove ALL wrong products
        print("🗑️  STEG 1: Fjerner ALLE feil produkter...")
        print()

        cart_url = f"{cart.BASE_URL}/cart/"
        await cart.page.goto(cart_url, wait_until="networkidle")
        await asyncio.sleep(2)

        removed_count = 0

        for iteration in range(20):
            articles = await cart.page.query_selector_all('article')

            if not articles:
                break

            found_to_remove = False

            for article in articles:
                try:
                    text = await article.inner_text()
                    product_name = text.split('\n')[0].strip() if text else ""

                    # Skip error messages
                    if "må fjerne" in product_name.lower():
                        continue

                    should_remove = False
                    matched_keyword = ""

                    for keyword in REMOVE_ALL_WRONG:
                        if keyword.lower() in text.lower():
                            should_remove = True
                            matched_keyword = keyword
                            break

                    if should_remove:
                        print(f"❌ Fjerner: {product_name[:60]} (grunn: {matched_keyword})")

                        all_buttons = await article.query_selector_all('button')

                        for btn in all_buttons:
                            try:
                                aria_label = await btn.get_attribute('aria-label') or ""

                                if 'fjern' in aria_label.lower():
                                    await btn.click()
                                    await asyncio.sleep(0.5)
                                    removed_count += 1
                                    found_to_remove = True
                                    break

                            except:
                                continue

                        if found_to_remove:
                            break

                except:
                    continue

            if not found_to_remove:
                break

            await cart.page.reload(wait_until="networkidle")
            await asyncio.sleep(2)

        print(f"\n✅ Fjernet {removed_count} feil produkter\n")

        # STEP 2: Add correct products
        print("🛒 STEG 2: Legger til RIKTIGE produkter...")
        print()

        added = 0
        failed = 0

        for product_name, qty in CORRECT_PRODUCTS:
            print(f"{product_name} x{qty}... ", end='', flush=True)

            success = await cart.add_product_by_search(product_name, quantity=qty)

            if success:
                print("✅")
                added += 1
            else:
                print("❌")
                failed += 1

            await asyncio.sleep(1)

        print()
        print("="*80)
        print("ENDELIG RESULTAT")
        print("="*80)
        print(f"🗑️  Fjernet: {removed_count} feil produkter")
        print(f"✅ Lagt til: {added}/{len(CORRECT_PRODUCTS)} riktige produkter")
        print("="*80)
        print()
        print("💰 HANDLEKURV BØR NÅ VÆRE:")
        print()
        print("   ✅ Løk (~17 kr)")
        print("   ✅ Hvitløk (~18 kr)")
        print("   ✅ Gulrot (~20 kr)")
        print("   ✅ Poteter (~35 kr)")
        print("   ✅ Hakkede tomater x2 (~30 kr)")
        print("   ✅ Kjøttdeig x2 (~130 kr)")
        print("   ✅ Pølser (~83 kr)")
        print("   ✅ Melk lett (~36 kr)")
        print("   ✅ Kremfløte laktosefri (~30 kr)")
        print("   ✅ Pasta x2 (~80 kr)")
        print("   ✅ Ris (~30 kr)")
        print("   ✅ Kidney beans (~16 kr)")
        print("   ✅ Taco krydder (~20 kr)")
        print("   ✅ Buljong (~20 kr)")
        print()
        print("💰 TOTAL: ~565 kr ✅✅✅")
        print()
        print("📝 4 BILLIGE MIDDAGER KLARE!")
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
