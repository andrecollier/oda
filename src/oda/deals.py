"""Oda.no deals scraper using Playwright."""

import asyncio
import re
from urllib.parse import urljoin

from playwright.async_api import Page, async_playwright

from .models import Deal, ProductAlternative


class OdaDealsManager:
    """Scrape and manage deals from Oda.no weekly discounts page."""

    BASE_URL = "https://oda.com/no"
    DEALS_URL = f"{BASE_URL}/products/discounts/"

    def __init__(self, email: str, password: str, headless: bool = True):
        """Initialize Oda deals manager.

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
        self._deals_cache: list[Deal] = []  # Cache deals for session

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

            # Fill in credentials
            await self.page.fill('#email-input', self.email)
            await self.page.fill('#password-input', self.password)

            # Submit form
            button = await self.page.query_selector('button:has-text("Logg inn")')
            if button:
                await button.evaluate("element => element.click()")

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

    def _parse_discount_text(self, badge_text: str) -> tuple[str, float]:
        """Parse discount badge text to extract type and value.

        Args:
            badge_text: Text from discount badge (e.g., "30%", "2 for 1")

        Returns:
            Tuple of (discount_type, discount_value)
        """
        badge_text = badge_text.lower().strip()

        # Percentage discount: "30%", "30 %", etc.
        if match := re.search(r'(\d+)\s*%', badge_text):
            return ("percentage", float(match.group(1)))

        # 2-for-1 type: "2 for 1", "2 for kr", etc.
        if match := re.search(r'(\d+)\s*for\s*(\d+)', badge_text):
            buy = int(match.group(1))
            pay = int(match.group(2))
            return (f"{buy}-for-{pay}", float(buy))

        # 3 for 2 type: "3 for 2"
        if "3 for 2" in badge_text or "3 for kr 2" in badge_text:
            return ("3-for-2", 3.0)

        # Default to percentage if we see a number
        if match := re.search(r'(\d+)', badge_text):
            return ("fixed", float(match.group(1)))

        return ("unknown", 0.0)

    def _parse_price(self, price_text: str) -> float | None:
        """Parse price text to float.

        Args:
            price_text: Price text (e.g., "kr 29.90", "29,90")

        Returns:
            Price as float or None if parsing fails
        """
        if not price_text:
            return None

        # Remove "kr", spaces, and convert comma to dot
        price_text = price_text.lower().replace("kr", "").replace(",", ".").strip()

        try:
            # Extract first number (handles cases like "29.90/kg")
            if match := re.search(r'(\d+\.?\d*)', price_text):
                return float(match.group(1))
        except (ValueError, AttributeError):
            pass

        return None

    async def scrape_weekly_deals(self, force_refresh: bool = False) -> list[Deal]:
        """Scrape all products from weekly deals page.

        Args:
            force_refresh: Force re-scraping even if cache exists

        Returns:
            List of Deal objects with product info, prices, discount type
        """
        if not self.page:
            raise RuntimeError("Browser not started. Call start() first.")

        # Return cached deals if available and not forcing refresh
        if self._deals_cache and not force_refresh:
            return self._deals_cache

        if not self._is_logged_in:
            await self.login()

        try:
            print(f"Scraping deals from: {self.DEALS_URL}")
            await self.page.goto(self.DEALS_URL, wait_until="networkidle")

            # Scroll to load all deals (infinite scroll)
            previous_count = 0
            max_scrolls = 20

            for i in range(max_scrolls):
                await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(1)

                # Count product cards
                product_cards_list = await self.page.query_selector_all('article')
                product_cards = len(product_cards_list)

                if product_cards >= previous_count and i > 0:
                    # No new products loaded
                    break

                previous_count = product_cards

            print(f"  Found {previous_count} product cards on deals page")

            # Extract deals from product cards
            deals = []
            product_cards = await self.page.query_selector_all('article')

            for card in product_cards:
                try:
                    # Get all text from card
                    card_text = await card.inner_text()

                    # Extract product name
                    name_elem = await card.query_selector('h2, h3, [class*="product-name"], [class*="product-title"]')
                    if name_elem:
                        name = (await name_elem.inner_text()).strip()
                    else:
                        # Fallback: use first line
                        lines = [l.strip() for l in card_text.split('\n') if l.strip()]
                        name = lines[0] if lines else None

                    if not name:
                        continue

                    # Extract prices using regex on all text
                    # Look for "kr XX.XX" patterns
                    price_matches = re.findall(r'kr\s*(\d+[.,]\d{2})', card_text, re.IGNORECASE)

                    # Usually first match is sale price, second (if exists) is original
                    sale_price = None
                    original_price = None

                    if len(price_matches) >= 1:
                        sale_price = float(price_matches[0].replace(",", "."))

                    if len(price_matches) >= 2:
                        # If there are two prices, second is likely original (crossed out)
                        original_price = float(price_matches[1].replace(",", "."))

                    # Skip if we can't find sale price
                    if sale_price is None:
                        continue

                    # If no original price found, estimate it (assume at least 10% discount)
                    if original_price is None:
                        original_price = sale_price * 1.1

                    # Extract discount badge
                    discount_type = "percentage"
                    discount_value = 10.0

                    badge = await card.query_selector('[class*="discount"], [class*="badge"], [class*="label"]')
                    if badge:
                        badge_text = await badge.inner_text()
                        discount_type, discount_value = self._parse_discount_text(badge_text)

                    # Extract product URL
                    link = await card.query_selector('a')
                    url = await link.get_attribute('href') if link else None

                    # Extract image
                    img = await card.query_selector('img')
                    image_url = await img.get_attribute('src') if img else None

                    deal = Deal(
                        product_name=name,
                        product_url=urljoin(self.BASE_URL, url) if url else "",
                        original_price=original_price,
                        sale_price=sale_price,
                        discount_type=discount_type,
                        discount_value=discount_value,
                        image_url=image_url,
                    )

                    deals.append(deal)

                except Exception as e:
                    # Skip problematic cards
                    print(f"  Warning: Failed to parse product card: {e}")
                    continue

            print(f"  Extracted {len(deals)} deals")

            # Cache the deals
            self._deals_cache = deals

            return deals

        except Exception as e:
            print(f"Failed to scrape deals: {e}")
            return []

    async def get_deal_info(self, product_name: str) -> Deal | None:
        """Check if a product is in current weekly deals.

        Args:
            product_name: Product name to check (case-insensitive)

        Returns:
            Deal object if found, None otherwise
        """
        # Ensure we have deals scraped
        if not self._deals_cache:
            await self.scrape_weekly_deals()

        # Fuzzy match product name
        product_name_lower = product_name.lower()

        for deal in self._deals_cache:
            # Check if product names match (fuzzy)
            if product_name_lower in deal.product_name.lower() or \
               deal.product_name.lower() in product_name_lower:
                return deal

        return None

    async def search_product_alternatives(
        self,
        ingredient_name: str,
        cart_manager,  # OdaCartManager instance
        limit: int = 5
    ) -> list[ProductAlternative]:
        """Search for product alternatives for an ingredient.

        This method combines:
        1. Searching Oda for the ingredient
        2. Extracting multiple results with prices
        3. Checking if products are on weekly deals
        4. Sorting by deals first, then price

        Args:
            ingredient_name: The ingredient to search for
            cart_manager: OdaCartManager instance to use for searching
            limit: Maximum number of alternatives to return

        Returns:
            List of ProductAlternative objects sorted by value
        """
        # Ensure deals are scraped
        if not self._deals_cache:
            await self.scrape_weekly_deals()

        # Search for products using cart manager
        search_results = await cart_manager.search_products(ingredient_name, limit=limit)

        # Convert to ProductAlternative objects and check for deals
        alternatives = []

        for result in search_results:
            # Check if this product is on deal
            deal_info = await self.get_deal_info(result['name'])

            alternative = ProductAlternative(
                name=result['name'],
                price=result['price'],
                unit_price_text=result.get('unit_price_text'),
                product_url=result['product_url'],
                is_on_deal=deal_info is not None,
                deal_info=deal_info,
                is_bulk=result.get('is_bulk', False),
                is_precut=result.get('is_precut', False),
            )

            alternatives.append(alternative)

        # Sort: deals first (with highest discount), then by price
        alternatives.sort(key=lambda x: (
            not x.is_on_deal,  # Deals first (False < True)
            -x.savings_percentage if x.is_on_deal else 0,  # Highest discount first
            x.price  # Then by price (lowest first)
        ))

        return alternatives
