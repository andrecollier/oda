"""Simple focused demo of core Oda Meal Planner features."""

import asyncio

from src.config import settings
from src.oda.cart import OdaCartManager
from src.kassal.client import KassalClient
from src.kassal.models import ProductSearchParams


async def demo_shopping_workflow():
    """Demonstrate product search and cart management."""
    print("\n" + "=" * 70)
    print("🍽️  Oda Meal Planner - Shopping Workflow Demo")
    print("=" * 70)

    # Step 1: Search products via Kassal API
    print("\n🔍 Step 1: Searching Products via Kassal.app API")
    print("-" * 70)

    shopping_list = [
        "melk",
        "brød",
        "egg",
        "smør",
        "ost"
    ]

    products_to_add = []

    async with KassalClient(api_key=settings.kassal_api_key) as client:
        for item in shopping_list:
            params = ProductSearchParams(search=item, size=3)
            results = await client.search_products(params)

            if results.data:
                print(f"\n✅ '{item}' - Found {len(results.data)} products:")
                for i, product in enumerate(results.data[:2], 1):
                    price_str = f"{product.current_price} kr" if product.current_price else "N/A"
                    print(f"   {i}. {product.name}")
                    print(f"      Brand: {product.brand or 'N/A'} | Price: {price_str}")

                # Add first result to our list
                products_to_add.append(item)
            else:
                print(f"\n⚠️  No products found for '{item}'")

    # Step 2: Login to Oda and add products to cart
    print("\n\n🛒 Step 2: Adding Products to Oda.no Cart")
    print("-" * 70)

    async with OdaCartManager(
        email=settings.oda_email,
        password=settings.oda_password,
        headless=False
    ) as cart:
        print("🔐 Logging in to Oda.no...")
        login_success = await cart.login()

        if not login_success:
            print("❌ Login failed!")
            return

        print(f"✅ Login successful! ({settings.oda_email})\n")

        # Add products to cart
        success_count = 0
        for product_name in products_to_add[:3]:  # Add first 3 items
            print(f"📦 Adding '{product_name}' to cart...")
            success = await cart.add_product_by_search(product_name, quantity=1)

            if success:
                print(f"   ✅ Added successfully")
                success_count += 1
            else:
                print(f"   ⚠️  Could not add")

            # Small delay between products
            await cart.page.wait_for_timeout(1000)

        print(f"\n✅ Added {success_count}/{len(products_to_add[:3])} products to cart")

        # Step 3: Preview the cart
        print("\n\n👁️  Step 3: Cart Preview")
        print("-" * 70)
        print("🌐 Opening cart in browser...")
        print("   (You can see all products and prices)")
        print("   Browser will stay open for 10 seconds...\n")

        # Navigate to cart
        cart_url = f"{cart.BASE_URL}/cart/"
        await cart.page.goto(cart_url, wait_until="networkidle")

        # Wait so user can see the cart
        await cart.page.wait_for_timeout(10000)

        # Try to get cart items
        print("\n📊 Cart Summary:")
        print("-" * 70)

        items = await cart.get_cart_items()

        if items:
            print(f"✅ Cart contains {len(items)} item(s):\n")
            for i, item in enumerate(items, 1):
                print(f"   {i}. {item['name']}")
                print(f"      Quantity: {item['quantity']}")
                print(f"      Price: {item['price']}")
        else:
            print("ℹ️  Cart items shown in browser")
            print("   (Item extraction may need selector updates)")

    # Final summary
    print("\n\n" + "=" * 70)
    print("🎉 Demo Complete!")
    print("=" * 70)
    print("\n✅ Successfully demonstrated:")
    print("   • Product search via Kassal.app API")
    print("   • Login to Oda.no")
    print("   • Adding multiple products to cart")
    print("   • Visual cart preview")
    print("\n📝 Next steps:")
    print("   • Review cart in browser")
    print("   • Adjust quantities if needed")
    print("   • Complete checkout manually when ready")
    print("\n⚠️  Important: Automatic checkout is disabled as a safety guardrail.")
    print("   You must complete the purchase manually in the browser.")
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    asyncio.run(demo_shopping_workflow())
