"""Oda.no shopping cart manager using Playwright."""

from playwright.async_api import Page, async_playwright
from urllib.parse import urljoin


class OdaCartManager:
    """Manage Oda.no shopping cart using Playwright."""

    BASE_URL = "https://oda.com/no"

    def __init__(self, email: str, password: str, headless: bool = True):
        """Initialize Oda cart manager.

        Args:
            email: Oda.no account email
            password: Oda.no account password
            headless: Run browser in headless mode (default: True)
        """
        self.email = email
        self.password = password
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None
        self.page: Page | None = None
        self._is_logged_in = False

    async def __aenter__(self):
        """Context manager entry - start browser."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close browser."""
        await self.close()

    async def start(self):
        """Start browser session."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        self.context = await self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        )
        self.page = await self.context.new_page()

    async def close(self):
        """Close browser session."""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def login(self) -> bool:
        """Login to Oda.no.

        Returns:
            True if login successful, False otherwise
        """
        if not self.page:
            raise RuntimeError("Browser not started. Call start() first.")

        if self._is_logged_in:
            return True

        try:
            # Go directly to login page
            login_url = f"{self.BASE_URL}/user/login/"
            await self.page.goto(login_url, wait_until="networkidle")

            # Wait for login form (try multiple selectors)
            email_selectors = [
                'input[type="email"]',
                'input[name="email"]',
                'input[name="username"]',
                'input[id="email"]',
                '#email',
            ]

            email_input = None
            for selector in email_selectors:
                try:
                    email_input = await self.page.wait_for_selector(selector, timeout=5000)
                    if email_input:
                        break
                except Exception:
                    continue

            if not email_input:
                # If still not found, take a screenshot for debugging
                await self.page.screenshot(path="login_page_debug.png")
                raise RuntimeError("Could not find email input field. Screenshot saved to login_page_debug.png")

            # Fill in credentials using correct IDs
            await self.page.fill('#email-input', self.email)
            await self.page.fill('#password-input', self.password)

            # Submit form - look for submit button
            submit_selectors = [
                'button[type="submit"]',
                'button:has-text("Logg inn")',
                'button:has-text("Log in")',
                'input[type="submit"]',
            ]

            for selector in submit_selectors:
                try:
                    await self.page.click(selector, timeout=5000)
                    break
                except Exception:
                    continue

            # Wait for navigation after login
            await self.page.wait_for_load_state("networkidle")

            # Check if login was successful
            is_logged_in = (
                await self.page.locator(
                    'a[href*="account"], button:has-text("Min konto")'
                ).count()
                > 0
            )

            self._is_logged_in = is_logged_in
            return is_logged_in

        except Exception as e:
            print(f"Login failed: {e}")
            return False

    async def add_product_by_url(self, product_url: str, quantity: int = 1) -> bool:
        """Add a product to cart by navigating to its URL.

        Args:
            product_url: URL to product page on Oda.no
            quantity: Quantity to add (default: 1)

        Returns:
            True if product was added successfully
        """
        if not self.page:
            raise RuntimeError("Browser not started. Call start() first.")

        if not self._is_logged_in:
            await self.login()

        try:
            await self.page.goto(product_url, wait_until="networkidle")

            # Product page opens modal - look for "Legg til i handlekurven" button
            add_button_selectors = [
                'button:has-text("Legg til i handlekurven")',
                'button:has-text("Legg i handlekurv")',
                'button[aria-label*="Legg i handlekurv"]',
                'button.add-to-cart',
                '[data-testid="add-to-cart"]',
            ]

            # Set quantity if needed
            if quantity > 1:
                quantity_selectors = [
                    'input[type="number"]',
                    'input[aria-label*="Antall"]',
                    '.quantity-input',
                ]

                for selector in quantity_selectors:
                    try:
                        await self.page.fill(selector, str(quantity), timeout=3000)
                        break
                    except Exception:
                        continue

            # Click add to cart button
            for selector in add_button_selectors:
                try:
                    await self.page.click(selector, timeout=5000)
                    break
                except Exception:
                    continue

            # Wait a moment for cart to update
            await self.page.wait_for_timeout(2000)

            return True

        except Exception as e:
            print(f"Failed to add product {product_url}: {e}")
            return False

    async def add_product_by_search(self, product_name: str, quantity: int = 1) -> bool:
        """Add a product to cart by searching for it.

        Args:
            product_name: Name of product to search for
            quantity: Quantity to add (default: 1)

        Returns:
            True if product was added successfully
        """
        if not self.page:
            raise RuntimeError("Browser not started. Call start() first.")

        if not self._is_logged_in:
            await self.login()

        try:
            # Go to homepage
            await self.page.goto(self.BASE_URL, wait_until="networkidle")

            # Find and use search box
            search_input = await self.page.query_selector('input[type="search"]')
            if not search_input:
                print("Could not find search box")
                return False

            await search_input.fill(product_name)
            await search_input.press("Enter")

            # Wait for search results
            await self.page.wait_for_load_state("networkidle")
            await self.page.wait_for_timeout(2000)

            # Click on first product card to open modal
            product_card_selectors = [
                'article:first-child',  # First article (product card)
                '[data-testid="product-card"]:first-child',
                '.product-card:first-child',
                'a[href*="/products/"]:first-child',
            ]

            clicked = False
            for selector in product_card_selectors:
                try:
                    await self.page.click(selector, timeout=5000)
                    clicked = True
                    break
                except Exception:
                    continue

            if not clicked:
                print("Could not click on product card")
                return False

            # Wait for modal to open
            await self.page.wait_for_timeout(1000)

            # Now in modal - click "Legg til i handlekurven" button
            add_button_selectors = [
                'button:has-text("Legg til i handlekurven")',
                'button:has-text("Legg i handlekurv")',
            ]

            for selector in add_button_selectors:
                try:
                    await self.page.click(selector, timeout=5000)
                    print(f"✅ Clicked '{selector}'")
                    # Wait for cart to update
                    await self.page.wait_for_timeout(2000)
                    return True
                except Exception as e:
                    print(f"Could not click '{selector}': {e}")
                    continue

            return False

        except Exception as e:
            print(f"Failed to add product by search '{product_name}': {e}")
            return False

    async def get_cart_items(self) -> list[dict]:
        """Get items currently in the shopping cart.

        Returns:
            List of cart items with name, quantity, price
        """
        if not self.page:
            raise RuntimeError("Browser not started. Call start() first.")

        if not self._is_logged_in:
            await self.login()

        try:
            # Navigate to cart
            cart_url = f"{self.BASE_URL}/cart/"
            await self.page.goto(cart_url, wait_until="networkidle")

            # Parse cart items
            items = []
            item_selectors = [
                '.cart-item',
                '[data-testid="cart-item"]',
                '.checkout-item',
            ]

            for selector in item_selectors:
                elements = await self.page.query_selector_all(selector)
                if elements:
                    for elem in elements:
                        try:
                            name = await elem.query_selector(".product-name, .item-name")
                            quantity = await elem.query_selector(".quantity, .item-quantity")
                            price = await elem.query_selector(".price, .item-price")

                            items.append(
                                {
                                    "name": await name.inner_text() if name else "Unknown",
                                    "quantity": await quantity.inner_text() if quantity else "1",
                                    "price": await price.inner_text() if price else "N/A",
                                }
                            )
                        except Exception:
                            continue
                    break

            return items

        except Exception as e:
            print(f"Failed to get cart items: {e}")
            return []

    async def clear_cart(self) -> bool:
        """Clear all items from the shopping cart.

        Returns:
            True if cart was cleared successfully
        """
        if not self.page:
            raise RuntimeError("Browser not started. Call start() first.")

        if not self._is_logged_in:
            await self.login()

        try:
            # Navigate to cart
            cart_url = f"{self.BASE_URL}/cart/"
            await self.page.goto(cart_url, wait_until="networkidle")

            # Look for "Clear cart" or "Remove all" button
            clear_selectors = [
                'button:has-text("Tøm handlekurv")',
                'button:has-text("Fjern alle")',
                '[data-testid="clear-cart"]',
            ]

            for selector in clear_selectors:
                try:
                    await self.page.click(selector, timeout=5000)

                    # Confirm if there's a confirmation dialog
                    confirm_selectors = ['button:has-text("Ja")', 'button:has-text("Bekreft")']

                    for confirm_selector in confirm_selectors:
                        try:
                            await self.page.click(confirm_selector, timeout=3000)
                            break
                        except Exception:
                            continue

                    return True
                except Exception:
                    continue

            return False

        except Exception as e:
            print(f"Failed to clear cart: {e}")
            return False

    async def preview_cart(self, pause: bool = True) -> str:
        """Open browser and show cart for visual preview.

        Browser will remain open until manually closed.

        Args:
            pause: If True, pauses execution with Playwright Inspector (default: True)

        Returns:
            Message with instructions
        """
        if not self.page:
            raise RuntimeError("Browser not started. Call start() first.")

        if not self._is_logged_in:
            await self.login()

        # Navigate to cart
        cart_url = f"{self.BASE_URL}/checkout/cart"
        await self.page.goto(cart_url, wait_until="networkidle")

        if pause:
            # Open Playwright Inspector and pause
            # User can inspect page and resume when ready
            await self.page.pause()

        return (
            "✅ Browser åpnet med handlekurv!\n\n"
            "Nettleseren viser nå din Oda handlekurv.\n"
            "Du kan se alle produkter, priser og totalt.\n\n"
            "Playwright Inspector er åpnet:\n"
            "- Klikk 'Resume' (▶️) for å fortsette og lukke browseren\n"
            "- Eller lukk både Inspector og nettleservinduet manuelt"
        )

    async def checkout_guardrail(self) -> dict:
        """Show cart summary and wait for user confirmation before checkout.

        This is the GUARDRAIL - prevents automatic checkout.

        Returns:
            Dictionary with cart summary and total price
        """
        items = await self.get_cart_items()

        # Navigate to checkout page (but don't complete)
        checkout_url = f"{self.BASE_URL}/checkout"
        await self.page.goto(checkout_url, wait_until="networkidle")

        # Extract total price
        total_price = "N/A"
        try:
            total_element = await self.page.query_selector(
                '.total-price, [data-testid="total-price"]'
            )
            if total_element:
                total_price = await total_element.inner_text()
        except Exception:
            pass

        return {
            "items": items,
            "total_price": total_price,
            "status": "READY_FOR_CHECKOUT",
            "message": "Cart is ready. User must manually complete checkout in browser.",
        }
