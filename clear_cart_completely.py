#!/usr/bin/env python3
"""Clear entire cart - remove ALL products."""

import asyncio
from src.config import settings
from src.oda.cart import OdaCartManager


async def main():
    """Clear entire shopping cart."""
    print("="*80)
    print("🗑️  TØMMER HELE HANDLEKURVEN")
    print("="*80)
    print()
    print("Dette vil fjerne ALLE produkter fra handlekurven")
    print("Så kan vi starte på nytt med billigere oppskrifter!")
    print()

    async with OdaCartManager(
        settings.oda_email,
        settings.oda_password,
        headless=False
    ) as cart:

        await cart.login()
        print("✅ Innlogget!\n")

        cart_url = f"{cart.BASE_URL}/cart/"
        await cart.page.goto(cart_url, wait_until="networkidle")
        await asyncio.sleep(3)

        removed_count = 0
        removed_items = []

        print("Fjerner alle produkter...\n")

        # Keep removing until cart is empty
        for iteration in range(50):  # Max 50 products
            articles = await cart.page.query_selector_all('article')

            if not articles:
                print("Ingen flere produkter!")
                break

            removed_this_iteration = False

            for article in articles:
                try:
                    text = await article.inner_text()
                    lines = text.split('\n')
                    product_name = lines[0].strip() if lines else "Ukjent"

                    # Skip error messages
                    if "må fjerne" in product_name.lower():
                        continue

                    # Find remove button
                    all_buttons = await article.query_selector_all('button')

                    for btn in all_buttons:
                        try:
                            btn_text = await btn.inner_text()
                            aria_label = await btn.get_attribute('aria-label') or ""

                            is_remove = (
                                btn_text.strip() in ['×', 'X', 'x'] or
                                'fjern' in btn_text.lower() or
                                'fjern' in aria_label.lower() or
                                'remove' in aria_label.lower()
                            )

                            if is_remove:
                                print(f"❌ Fjerner: {product_name[:60]}")
                                await btn.click()
                                await asyncio.sleep(0.5)
                                removed_count += 1
                                removed_items.append(product_name[:50])
                                removed_this_iteration = True
                                break

                        except:
                            continue

                    if removed_this_iteration:
                        break

                except:
                    continue

            if not removed_this_iteration:
                # No more products to remove
                break

            # Reload
            await cart.page.reload(wait_until="networkidle")
            await asyncio.sleep(2)

        print()
        print("="*80)
        print(f"✅ TØMT! Fjernet {removed_count} produkter")
        print("="*80)
        print()

        if removed_count > 0:
            print("Handlekurven er nå TOM!")
            print()
            print("Neste steg: Søke etter BILLIGE oppskrifter på Oda.no")
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
