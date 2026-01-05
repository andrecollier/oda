"""Oda.no order history scraper using Playwright."""

import asyncio
import re
from datetime import datetime
from typing import Any
from urllib.parse import urljoin

from playwright.async_api import Page, async_playwright


class OdaOrderScraper:
    """Scrape order history from Oda.no account/orders page."""

    BASE_URL = "https://oda.com/no"
    ORDERS_URL = f"{BASE_URL}/account/orders/"

    def __init__(self, email: str, password: str, headless: bool = True):
        """Initialize Oda order scraper.

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

    async def _dismiss_cookie_popup(self):
        """Dismiss cookie consent popup if present."""
        if not self.page:
            return

        try:
            cookie_selectors = [
                'button:has-text("Godta alle")',
                'button:has-text("Aksepter")',
                'button:has-text("Jeg forstår")',
                'button:has-text("OK")',
                '[id*="cookie"] button:has-text("Accept")',
                '[class*="cookie"] button',
                '[data-testid*="cookie-accept"]',
                '[aria-label*="cookie" i]',
            ]

            for selector in cookie_selectors:
                try:
                    button = await self.page.query_selector(selector)
                    if button:
                        await button.click()
                        await self.page.wait_for_timeout(1000)
                        print(f"✓ Dismissed cookie popup")
                        return
                except Exception:
                    continue
        except Exception:
            pass

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

            # Dismiss cookie popup if present
            await self._dismiss_cookie_popup()

            # Fill in credentials
            await self.page.fill('#email-input', self.email)
            await self.page.fill('#password-input', self.password)

            # Submit form
            submit_selectors = [
                'button[type="submit"]',
                'button:has-text("Logg inn")',
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
            is_logged_in = await self.page.locator(
                'a[href*="account"], button:has-text("Min konto")'
            ).count() > 0

            self._is_logged_in = is_logged_in
            return is_logged_in

        except Exception as e:
            print(f"Login failed: {e}")
            return False

    async def scrape_orders(self, max_orders: int = 100) -> list[dict]:
        """Scrape all orders from the orders page.

        Args:
            max_orders: Maximum number of orders to scrape (default: 100)

        Returns:
            List of order dictionaries with order_number, date, items, total
        """
        if not self.page:
            raise RuntimeError("Browser not started. Call start() first.")

        if not self._is_logged_in:
            await self.login()

        try:
            # Navigate to orders page
            await self.page.goto(self.ORDERS_URL, wait_until="networkidle")
            await self._dismiss_cookie_popup()

            # Wait for orders to load
            await self.page.wait_for_timeout(2000)

            # Scroll to load more orders (if paginated)
            previous_count = 0
            max_scrolls = 20

            for _ in range(max_scrolls):
                # Scroll to bottom
                await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(1)

                # Count order cards/links
                order_elements = await self.page.locator('[class*="order"], [data-testid*="order"], article').all()
                current_count = len(order_elements)

                if current_count >= max_orders or current_count == previous_count:
                    break

                previous_count = current_count

            # Extract order data
            orders = []
            order_elements = await self.page.locator('[class*="order"], article').all()

            print(f"Found {len(order_elements)} order elements on page")

            for i, order_elem in enumerate(order_elements[:max_orders]):
                try:
                    # Extract order text content
                    order_text = await order_elem.inner_text()

                    # Extract order number (look for patterns like "Ordre #123456" or just numbers)
                    order_number_match = re.search(r'(?:Ordre|Order)\s*#?(\d+)', order_text, re.IGNORECASE)
                    if not order_number_match:
                        order_number_match = re.search(r'#(\d+)', order_text)

                    if not order_number_match:
                        print(f"  ⚠ Skipping order {i+1}: No order number found")
                        continue

                    order_number = order_number_match.group(1)

                    # Extract date (look for date patterns)
                    date_match = re.search(r'(\d{1,2})[.\s]+([a-zæøå]+)[.\s]+(\d{4})', order_text, re.IGNORECASE)
                    order_date = None
                    if date_match:
                        day, month_name, year = date_match.groups()
                        # Convert Norwegian month names to month number
                        month_map = {
                            'januar': 1, 'februar': 2, 'mars': 3, 'april': 4,
                            'mai': 5, 'juni': 6, 'juli': 7, 'august': 8,
                            'september': 9, 'oktober': 10, 'november': 11, 'desember': 12
                        }
                        month = month_map.get(month_name.lower(), 1)
                        order_date = datetime(int(year), month, int(day))

                    # Extract total price (look for "kr" patterns)
                    total_price = None
                    price_matches = re.findall(r'(?:kr\s*)?(\d+[.,]\d{2})', order_text)
                    if price_matches:
                        # Take the largest price as the total (heuristic)
                        prices = [float(p.replace(',', '.')) for p in price_matches]
                        total_price = max(prices)

                    # Try to click order to get items (if clickable)
                    items = []
                    try:
                        # Look for clickable link or button
                        link = await order_elem.query_selector('a, button')
                        if link:
                            # Get the order detail page URL
                            href = await link.get_attribute('href')
                            if href and '/orders/' in href:
                                detail_url = urljoin(self.BASE_URL, href)
                                items = await self._scrape_order_detail(detail_url)
                    except Exception as e:
                        print(f"  ⚠ Could not get order details for order {order_number}: {e}")

                    orders.append({
                        'order_number': order_number,
                        'order_date': order_date,
                        'total_price': total_price,
                        'status': 'delivered',  # Assume delivered if in history
                        'items': items
                    })

                    print(f"  ✓ Scraped order {order_number} ({order_date.strftime('%Y-%m-%d') if order_date else 'unknown date'})")

                except Exception as e:
                    print(f"  ✗ Failed to parse order {i+1}: {e}")
                    continue

            return orders

        except Exception as e:
            print(f"Failed to scrape orders: {e}")
            return []

    async def _scrape_order_detail(self, detail_url: str) -> list[dict]:
        """Scrape items from an order detail page.

        Args:
            detail_url: URL to order detail page

        Returns:
            List of item dictionaries with name, quantity, price
        """
        try:
            # Navigate to order detail page
            await self.page.goto(detail_url, wait_until="networkidle")
            await self.page.wait_for_timeout(1000)

            items = []

            # Look for product items in the order
            product_elements = await self.page.locator('[class*="product"], [class*="item"], tr, li').all()

            for elem in product_elements:
                try:
                    elem_text = await elem.inner_text()

                    # Skip if too short (likely not a product)
                    if len(elem_text.strip()) < 5:
                        continue

                    # Extract product name (first line or prominent text)
                    lines = [l.strip() for l in elem_text.split('\n') if l.strip()]
                    if not lines:
                        continue

                    product_name = lines[0]

                    # Skip header rows or non-product text
                    if any(skip in product_name.lower() for skip in ['produkt', 'antall', 'pris', 'sum', 'totalt']):
                        continue

                    # Extract quantity
                    quantity = 1
                    quantity_match = re.search(r'(\d+)\s*(?:stk|x|kg|g|l|ml)', elem_text, re.IGNORECASE)
                    if quantity_match:
                        quantity = int(quantity_match.group(1))

                    # Extract price
                    price = None
                    price_match = re.search(r'kr\s*(\d+[.,]\d{2})', elem_text, re.IGNORECASE)
                    if price_match:
                        price = float(price_match.group(1).replace(',', '.'))

                    if product_name and len(product_name) > 2:
                        items.append({
                            'product_name': product_name,
                            'quantity': quantity,
                            'price': price
                        })

                except Exception:
                    continue

            # Navigate back to orders page
            await self.page.goto(self.ORDERS_URL, wait_until="networkidle")
            await self.page.wait_for_timeout(1000)

            return items[:20]  # Limit to 20 items per order

        except Exception as e:
            print(f"  ⚠ Failed to scrape order detail: {e}")
            return []
