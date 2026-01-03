"""Test script for Oda Meal Planner system."""

import asyncio
from src.config import settings
from src.oda.cart import OdaCartManager
from src.kassal.client import KassalClient
from src.kassal.models import ProductSearchParams


async def test_oda_login():
    """Test Oda.no login."""
    print("\n🧪 Test 1: Oda.no Login")
    print("=" * 50)

    async with OdaCartManager(
        email=settings.oda_email,
        password=settings.oda_password,
        headless=False  # Show browser for testing
    ) as cart:
        success = await cart.login()

        if success:
            print("✅ Login successful!")
            print(f"   Email: {settings.oda_email}")
            return True
        else:
            print("❌ Login failed!")
            return False


async def test_kassal_api():
    """Test Kassal.app API product search."""
    print("\n🧪 Test 2: Kassal.app API Product Search")
    print("=" * 50)

    async with KassalClient(api_key=settings.kassal_api_key) as client:
        # Search for a simple product
        params = ProductSearchParams(
            search="agurk",
            size=3
        )
        results = await client.search_products(params)

        if results and results.data:
            print(f"✅ Found {len(results.data)} products")
            for i, product in enumerate(results.data[:3], 1):
                print(f"\n   {i}. {product.name}")
                print(f"      Brand: {product.brand or 'N/A'}")
                print(f"      Price: {product.current_price} kr" if product.current_price else "      Price: N/A")
                print(f"      Vendor: {product.vendor}")
            return True
        else:
            print("❌ No products found!")
            return False


async def test_add_to_cart():
    """Test adding product to Oda cart."""
    print("\n🧪 Test 3: Add Product to Cart")
    print("=" * 50)

    async with OdaCartManager(
        email=settings.oda_email,
        password=settings.oda_password,
        headless=False
    ) as cart:
        # Login first
        await cart.login()

        # Add a simple product
        print("   Searching for 'agurk' and adding to cart...")
        success = await cart.add_product_by_search("agurk", quantity=1)

        if success:
            print("✅ Product added to cart!")

            # Preview the cart
            print("\n   Opening cart preview...")
            await cart.preview_cart(pause=False)

            # Wait a bit to see the cart
            await cart.page.wait_for_timeout(5000)

            return True
        else:
            print("❌ Failed to add product!")
            return False


async def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 50)
    print("🧪 Oda Meal Planner System Tests")
    print("=" * 50)

    results = []

    # Test 1: Login
    try:
        result = await test_oda_login()
        results.append(("Oda Login", result))
    except Exception as e:
        print(f"❌ Login test failed with error: {e}")
        results.append(("Oda Login", False))

    # Test 2: API
    try:
        result = await test_kassal_api()
        results.append(("Kassal API", result))
    except Exception as e:
        print(f"❌ API test failed with error: {e}")
        results.append(("Kassal API", False))

    # Test 3: Add to cart
    try:
        result = await test_add_to_cart()
        results.append(("Add to Cart", result))
    except Exception as e:
        print(f"❌ Add to cart test failed with error: {e}")
        results.append(("Add to Cart", False))

    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("=" * 50)

    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:20} {status}")

    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)

    print(f"\nTotal: {total_passed}/{total_tests} tests passed")

    if total_passed == total_tests:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {total_tests - total_passed} test(s) failed")


if __name__ == "__main__":
    asyncio.run(run_all_tests())
