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
            await self.page.wait_for_timeout(500)
            await self.page.fill('#password-input', self.password)
            await self.page.wait_for_timeout(500)

            # Submit form - look for submit button and click with JavaScript
            submit_selectors = [
                'button:has-text("Logg inn")',
                'button[type="submit"]',
                'button:has-text("Log in")',
                'input[type="submit"]',
            ]

            button_clicked = False
            for selector in submit_selectors:
                try:
                    button = await self.page.query_selector(selector)
                    if button:
                        # Use JavaScript click for reliability
                        await button.evaluate("element => element.click()")
                        button_clicked = True
                        print(f"Clicked login button: {selector}")
                        break
                except Exception as e:
                    print(f"Could not click {selector}: {e}")
                    continue

            if not button_clicked:
                await self.page.screenshot(path="login_button_not_found.png")
                raise RuntimeError("Could not click login button")

            # Wait for navigation after login (longer timeout)
            await self.page.wait_for_timeout(3000)
            await self.page.wait_for_load_state("networkidle", timeout=15000)

            # Take screenshot after login attempt
            await self.page.screenshot(path="after_login_attempt.png")

            # Check if login was successful - multiple checks
            # Check 1: Look for "Min konto" or account links
            account_check = await self.page.locator(
                'a[href*="account"], button:has-text("Min konto")'
            ).count() > 0

            # Check 2: Make sure we're NOT still on login page
            current_url = self.page.url
            not_on_login_page = "/login" not in current_url

            # Check 3: Look for "Logg inn" button (if present, we're NOT logged in)
            login_button_visible = await self.page.locator('button:has-text("Logg inn")').count() > 0

            is_logged_in = account_check or (not_on_login_page and not login_button_visible)

            if not is_logged_in:
                await self.page.screenshot(path="login_failed_verification.png")
                print(f"Login verification failed:")
                print(f"  - Account check: {account_check}")
                print(f"  - Current URL: {current_url}")
                print(f"  - Login button still visible: {login_button_visible}")

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
            # CRITICAL: Reload homepage completely to reset ALL state
            await self.page.goto(self.BASE_URL, wait_until="domcontentloaded")
            await self.page.wait_for_timeout(2000)
            await self.page.wait_for_load_state("networkidle", timeout=10000)

            # Find and use search box
            search_input = await self.page.query_selector('input[type="search"]')
            if not search_input:
                print("Could not find search box")
                return False

            # CRITICAL: Clear search box completely first!
            await search_input.click()
            await search_input.fill("")  # Clear
            await self.page.wait_for_timeout(500)

            # Type the ACTUAL product name
            await search_input.type(product_name, delay=100)  # Slower typing
            await self.page.wait_for_timeout(500)

            # Submit search and wait for navigation to search results page
            current_url = self.page.url
            await search_input.press("Enter")

            # CRITICAL: Wait for URL to change to search results page
            # The URL should change from homepage to something like /search/?q=...
            try:
                await self.page.wait_for_url(
                    lambda url: url != current_url and ("/search" in url or "q=" in url),
                    timeout=10000
                )
                print(f"  ✓ Navigated to search results: {self.page.url}")
            except Exception:
                print(f"  ⚠ URL didn't change, may still be on homepage")

            # Wait for search results to load - CRITICAL!
            await self.page.wait_for_timeout(2000)  # Wait for search to complete
            await self.page.wait_for_load_state("networkidle", timeout=10000)
            await self.page.wait_for_timeout(1000)  # Extra wait for dynamic content

            # NEW STRATEGY: Find the "Legg til" button that belongs to our searched product
            # by checking the button's parent container for the product name
            # AVOID pre-cut/pre-packaged products (staver, kuttet, ferdig, etc.)
            try:
                # Get ALL "Legg til" buttons on the page
                all_buttons = await self.page.query_selector_all('button[aria-label*="Legg til"]')
                print(f"  Found {len(all_buttons)} 'Legg til' buttons on page")

                # Keywords to AVOID (pre-cut, pre-packaged, expensive options)
                avoid_keywords = [
                    "staver", "kuttet", "ferdig", "ferdigkuttet", "skåret",
                    "delt", "half", "halv", "mini", "mikro",
                    "juice", "drikke", "smoothie", "shot", "revet", "raspet",
                    "baby", "snack", "biter", "cubes", "terninger"
                ]

                # Keywords to PREFER (whole vegetables, bulk)
                prefer_keywords = [
                    "pose", "løsvekt", "kg", "hel", "hele", "pakke"
                ]

                clicked = False
                matching_products = []  # Store all matches to pick the best one

                for i, button in enumerate(all_buttons):
                    try:
                        # Get the button's parent article/container
                        parent = await button.evaluate_handle(
                            """button => {
                                // Walk up the DOM to find the article or product container
                                let el = button;
                                while (el && el.tagName !== 'ARTICLE' && el !== document.body) {
                                    el = el.parentElement;
                                }
                                return el;
                            }"""
                        )

                        if parent:
                            parent_text = await parent.evaluate("el => el.innerText")
                            parent_text_lower = parent_text.lower()

                            # Check if this parent contains our search term
                            if product_name.lower() in parent_text_lower:
                                # Check if it contains any avoid keywords
                                has_avoid_keyword = any(kw in parent_text_lower for kw in avoid_keywords)

                                # Check if it contains preferred keywords
                                has_prefer_keyword = any(kw in parent_text_lower for kw in prefer_keywords)

                                matching_products.append({
                                    "index": i,
                                    "button": button,
                                    "text": parent_text,
                                    "has_avoid_keyword": has_avoid_keyword,
                                    "has_prefer_keyword": has_prefer_keyword
                                })
                    except Exception as e:
                        print(f"  Error checking button {i+1}: {e}")
                        continue

                # Select the BEST match: prefer products WITH prefer keywords, WITHOUT avoid keywords
                if matching_products:
                    # Sort: prefer products with "pose/kg" keywords, avoid pre-cut keywords
                    # Priority: has_prefer_keyword (lower is better) -> has_avoid_keyword -> index
                    matching_products.sort(key=lambda x: (
                        not x["has_prefer_keyword"],  # Prefer products WITH prefer keywords (False < True)
                        x["has_avoid_keyword"],        # Avoid products with avoid keywords
                        x["index"]                     # Then by index (first result)
                    ))

                    best_match = matching_products[0]
                    if best_match["has_avoid_keyword"]:
                        print(f"  ⚠ Warning: Best match contains pre-cut keyword")
                    if best_match["has_prefer_keyword"]:
                        print(f"  ✓ Selected preferred option (pose/kg/løsvekt)")

                    print(f"  ✓ Found matching product in container {best_match['index']+1}")
                    print(f"    Product: {best_match['text'][:60]}...")

                    # Click THIS button
                    await best_match["button"].evaluate("button => button.click()")
                    print(f"  ✓ Clicked 'Legg til' button")
                    clicked = True
                    await self.page.wait_for_timeout(1500)
                    return True

                if not clicked:
                    print(f"  ✗ No button found for product '{product_name}'")
                    # Fallback: try clicking product card to open modal
                    print(f"  Trying fallback: click first article...")

                    article = await self.page.query_selector('main article:first-of-type')
                    if article:
                        await article.evaluate("el => el.click()")
                        await self.page.wait_for_timeout(2000)

                        # In modal, click "Legg til i handlekurven"
                        modal_button = await self.page.query_selector('button:has-text("Legg til i handlekurven")')
                        if modal_button:
                            await modal_button.evaluate("btn => btn.click()")
                            print(f"  ✓ Clicked via modal fallback")
                            await self.page.wait_for_timeout(1500)
                            return True

                    return False

            except Exception as e:
                print(f"  ✗ Error in button search: {e}")
                return False

        except Exception as e:
            print(f"Failed to add product by search '{product_name}': {e}")
            return False

    async def search_products(
        self,
        product_name: str,
        limit: int = 5
    ) -> list[dict]:
        """Search for products and return multiple results with prices.

        This is different from add_product_by_search - it RETURNS results
        instead of adding to cart.

        Args:
            product_name: Product to search for
            limit: Maximum number of results to return (default: 5)

        Returns:
            List of dicts with: name, price, unit_price_text, url, is_precut, is_bulk
        """
        if not self.page:
            raise RuntimeError("Browser not started. Call start() first.")

        if not self._is_logged_in:
            await self.login()

        try:
            # Reload homepage to reset state (same as add_product_by_search)
            await self.page.goto(self.BASE_URL, wait_until="domcontentloaded")
            await self.page.wait_for_timeout(2000)
            await self.page.wait_for_load_state("networkidle", timeout=10000)

            # Find and use search box
            search_input = await self.page.query_selector('input[type="search"]')
            if not search_input:
                print("Could not find search box")
                return []

            # Clear and type product name
            await search_input.click()
            await search_input.fill("")
            await self.page.wait_for_timeout(500)
            await search_input.type(product_name, delay=100)
            await self.page.wait_for_timeout(500)

            # Submit search
            current_url = self.page.url
            await search_input.press("Enter")

            # Wait for search results page
            try:
                await self.page.wait_for_url(
                    lambda url: url != current_url and ("/search" in url or "q=" in url),
                    timeout=10000
                )
            except Exception:
                pass

            # Wait for results to load
            await self.page.wait_for_timeout(2000)
            await self.page.wait_for_load_state("networkidle", timeout=10000)
            await self.page.wait_for_timeout(1000)

            # Extract product cards
            product_cards = await self.page.query_selector_all('main article')
            print(f"  Found {len(product_cards)} product cards")

            results = []

            # Keywords for quality checks
            avoid_keywords = [
                "staver", "kuttet", "ferdig", "ferdigkuttet", "skåret",
                "delt", "half", "halv", "mini", "mikro",
                "juice", "drikke", "smoothie", "shot", "revet", "raspet",
                "baby", "snack", "biter", "cubes", "terninger"
            ]

            prefer_keywords = [
                "pose", "løsvekt", "kg", "hel", "hele", "pakke"
            ]

            for i, card in enumerate(product_cards[:limit * 2]):  # Get extra to filter
                try:
                    # Get all text from card
                    card_text = await card.inner_text()

                    # Extract product name - first line or h2/h3
                    name_elem = await card.query_selector('h2, h3, [class*="product-title"], [class*="product-name"]')
                    if name_elem:
                        name = (await name_elem.inner_text()).strip()
                    else:
                        # Fallback: use first non-empty line
                        lines = [l.strip() for l in card_text.split('\n') if l.strip()]
                        name = lines[0] if lines else "Unknown"

                    # Extract price using regex on all card text
                    # Look for patterns like "kr 29.90", "29,90", etc.
                    import re
                    price = None

                    # Try to find "kr XX.XX" or "kr XX,XX"
                    price_matches = re.findall(r'kr\s*(\d+[.,]\d{2})', card_text, re.IGNORECASE)

                    if price_matches:
                        # Take the first price found (usually the main price)
                        price_str = price_matches[0].replace(",", ".")
                        try:
                            price = float(price_str)
                        except ValueError:
                            pass

                    # Extract unit price using regex
                    # Look for patterns like "kr 19.90/kg" or "19,90/kg"
                    unit_price_text = None
                    unit_price_matches = re.findall(r'(kr\s*\d+[.,]\d{2}/\w+)', card_text, re.IGNORECASE)
                    if unit_price_matches:
                        unit_price_text = unit_price_matches[0]

                    # Extract product URL
                    link = await card.query_selector('a')
                    url = await link.get_attribute('href') if link else None

                    # Quality checks
                    card_text_lower = card_text.lower()
                    is_precut = any(kw in card_text_lower for kw in avoid_keywords)
                    is_bulk = any(kw in card_text_lower for kw in prefer_keywords)

                    # Skip if no price found
                    if price is None:
                        continue

                    results.append({
                        'name': name,
                        'price': price,
                        'unit_price_text': unit_price_text,
                        'product_url': f"{self.BASE_URL}{url}" if url and url.startswith('/') else url,
                        'is_precut': is_precut,
                        'is_bulk': is_bulk,
                    })

                    if len(results) >= limit:
                        break

                except Exception as e:
                    print(f"  Warning: Failed to parse product card {i+1}: {e}")
                    continue

            print(f"  Extracted {len(results)} products with prices")
            return results

        except Exception as e:
            print(f"Failed to search products for '{product_name}': {e}")
            return []

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
        cart_url = f"{self.BASE_URL}/cart/"
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
