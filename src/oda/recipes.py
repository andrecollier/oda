"""Oda.no recipe scraper using Playwright."""

import asyncio
import re
from typing import Any
from urllib.parse import urljoin

from playwright.async_api import Page, async_playwright

from .models import Recipe, RecipeIngredient


class OdaRecipeScraper:
    """Scrape recipes from Oda.no using Playwright."""

    BASE_URL = "https://oda.com/no"
    RECIPES_URL = f"{BASE_URL}/recipes/"

    def __init__(self, email: str, password: str, headless: bool = True):
        """Initialize Oda recipe scraper.

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
        """Dismiss cookie consent popup if present.

        This is a reusable helper that can be called after page navigation
        to ensure a clean user experience in preview mode.
        """
        if not self.page:
            return

        try:
            # Common cookie popup selectors for Norwegian sites
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
                        print(f"✓ Dismissed cookie popup using selector: {selector}")
                        return
                except Exception:
                    continue
        except Exception as e:
            # Not critical - just log and continue
            print(f"Cookie popup dismissal attempt completed: {e}")

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

            # Check if login was successful (you're logged in if you see your account)
            is_logged_in = await self.page.locator(
                'a[href*="account"], button:has-text("Min konto")'
            ).count() > 0

            self._is_logged_in = is_logged_in
            return is_logged_in

        except Exception as e:
            print(f"Login failed: {e}")
            return False

    async def get_recipe_urls(
        self,
        filters: dict[str, Any] | None = None,
        limit: int = 20,
    ) -> list[str]:
        """Get URLs to recipes from the recipe listing page.

        Args:
            filters: Optional filters (e.g., {"category": "kylling"})
            limit: Maximum number of recipes to fetch

        Returns:
            List of recipe URLs
        """
        if not self.page:
            raise RuntimeError("Browser not started. Call start() first.")

        await self.page.goto(self.RECIPES_URL, wait_until="networkidle")

        # Apply filters if provided
        if filters:
            # This would need to be implemented based on Oda's actual filter UI
            pass

        # Scroll to load more recipes (infinite scroll)
        previous_count = 0
        max_scrolls = 10

        for _ in range(max_scrolls):
            await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(1)

            # Count recipe links
            recipe_links = await self.page.locator('a[href*="/recipes/"]').all()
            current_count = len(recipe_links)

            if current_count >= limit or current_count == previous_count:
                break

            previous_count = current_count

        # Extract URLs
        recipe_links = await self.page.locator('a[href*="/recipes/"]').all()
        urls = []

        for link in recipe_links[:limit * 2]:  # Get more to filter out plans/categories
            href = await link.get_attribute("href")
            if href and href not in urls:
                # SKIP plans/categories - only want actual recipes
                if "/plans/" in href or "/categories/" in href:
                    continue

                full_url = urljoin(self.BASE_URL, href)
                urls.append(full_url)

                if len(urls) >= limit:
                    break

        return urls

    async def scrape_recipe(self, url: str) -> Recipe | None:
        """Scrape a single recipe page.

        Args:
            url: URL to recipe page

        Returns:
            Recipe object or None if scraping failed
        """
        if not self.page:
            raise RuntimeError("Browser not started. Call start() first.")

        try:
            await self.page.goto(url, wait_until="networkidle")

            # Extract recipe ID from URL
            recipe_id = url.split("/recipes/")[-1].split("?")[0].strip("/")

            # Extract title
            title_element = await self.page.query_selector("h1")
            title = await title_element.inner_text() if title_element else "Unknown"

            # Extract image
            image_element = await self.page.query_selector('img[alt*="recipe"], main img')
            image_url = await image_element.get_attribute("src") if image_element else None

            # Extract description
            desc_element = await self.page.query_selector("p.description, .recipe-description")
            description = await desc_element.inner_text() if desc_element else None

            # Extract ingredients from accordion table
            ingredients = []

            # Find the ingredients accordion
            accordion = await self.page.query_selector('[data-test-id="accordion-ingredients"]')

            if accordion:
                # Open the accordion by clicking it (it's a details element)
                summary = await accordion.query_selector('summary')
                if summary:
                    await summary.click()
                    await self.page.wait_for_timeout(500)  # Wait for accordion to open

                # Find all table rows
                rows = await accordion.query_selector_all('tr')

                for row in rows:
                    # Get all td elements in this row
                    cells = await row.query_selector_all('td')

                    if len(cells) >= 2:
                        # First cell has quantity, second has name
                        quantity_elem = await cells[0].query_selector('span')
                        name_elem = await cells[1].query_selector('span.k-text-style--body-m')

                        if name_elem:
                            quantity_text = await quantity_elem.inner_text() if quantity_elem else ""
                            name_text = await name_elem.inner_text()

                            # Combine quantity and name
                            full_text = f"{quantity_text} {name_text}".strip() if quantity_text else name_text.strip()

                            # Try to find product link in the name cell
                            link = await cells[1].query_selector("a")
                            product_url = await link.get_attribute("href") if link else None

                            if full_text and not full_text.startswith("Foto"):  # Skip non-ingredient rows
                                ingredients.append(
                                    RecipeIngredient(
                                        name=full_text,
                                        product_url=urljoin(self.BASE_URL, product_url)
                                        if product_url
                                        else None,
                                    )
                                )

            # Extract instructions
            instructions = []
            instruction_elements = await self.page.query_selector_all(
                '[class*="instructionContainer"]'
            )

            for elem in instruction_elements:
                # Find the paragraph with instruction text
                p_elem = await elem.query_selector('p')
                if p_elem:
                    text = await p_elem.inner_text()
                    if text.strip():
                        instructions.append(text.strip())

            # Extract metadata
            servings = 4  # Default
            cooking_time = None
            difficulty = None

            # Try to extract servings
            servings_text = await self.page.locator(':text("porsjoner"), :text("Porsjoner")').first.text_content() if await self.page.locator(':text("porsjoner")').count() > 0 else None
            if servings_text:
                match = re.search(r"(\d+)", servings_text)
                if match:
                    servings = int(match.group(1))

            # Try to extract cooking time
            time_text = await self.page.locator(':text("min"), :text("timer")').first.text_content() if await self.page.locator(':text("min")').count() > 0 else None
            if time_text:
                cooking_time = time_text.strip()

            return Recipe(
                id=recipe_id,
                title=title.strip(),
                url=url,
                image_url=image_url,
                description=description,
                servings=servings,
                cooking_time=cooking_time,
                difficulty=difficulty,
                ingredients=ingredients,
                instructions=instructions,
            )

        except Exception as e:
            print(f"Failed to scrape recipe {url}: {e}")
            return None

    async def preview_recipes_page(self, pause: bool = True) -> str:
        """Open browser and show Oda recipes page for visual browsing.

        Browser will remain open until manually closed.

        Args:
            pause: If True, pauses with Playwright Inspector (default: True)

        Returns:
            Message with instructions
        """
        if not self.page:
            raise RuntimeError("Browser not started. Call start() first.")

        if not self._is_logged_in:
            await self.login()

        # Navigate to recipes page
        await self.page.goto(self.RECIPES_URL, wait_until="networkidle")

        # Dismiss cookie popup for clean preview
        await self._dismiss_cookie_popup()

        if pause:
            await self.page.pause()

        return (
            "✅ Browser åpnet med Oda oppskrifter!\n\n"
            "Nettleseren viser nå Oda.no/recipes siden.\n"
            "Du kan bla gjennom oppskrifter visuelt.\n\n"
            "Tips:\n"
            "- Bruk filtrene til venstre for å finne oppskrifter\n"
            "- Klikk på en oppskrift for å se detaljer\n\n"
            "Playwright Inspector er åpnet:\n"
            "- Klikk 'Resume' (▶️) når du er ferdig\n"
            "- Eller lukk både Inspector og nettleservinduet"
        )

    async def preview_recipe(self, url: str, pause: bool = True) -> str:
        """Open browser and show a specific recipe.

        Args:
            url: URL to recipe page
            pause: If True, pauses with Playwright Inspector (default: True)

        Returns:
            Message with instructions
        """
        if not self.page:
            raise RuntimeError("Browser not started. Call start() first.")

        if not self._is_logged_in:
            await self.login()

        await self.page.goto(url, wait_until="networkidle")

        # Dismiss cookie popup for clean preview
        await self._dismiss_cookie_popup()

        if pause:
            await self.page.pause()

        return (
            "✅ Browser åpnet med oppskrift!\n\n"
            "Nettleseren viser nå oppskriften.\n"
            "Du kan se:\n"
            "- Ingredienser\n"
            "- Fremgangsmåte\n"
            "- Bilder\n"
            "- Produktlenker\n\n"
            "Playwright Inspector er åpnet:\n"
            "- Klikk 'Resume' (▶️) når du er ferdig"
        )

    async def search_recipes(
        self,
        keywords: list[str] | None = None,
        family_friendly: bool = False,
        high_protein: bool = False,
        meal_prep: bool = False,
        limit: int = 10,
    ) -> list[Recipe]:
        """Search for recipes matching criteria.

        Args:
            keywords: Keywords to search for (e.g., ["kylling", "brokkoli"])
            family_friendly: Filter for family-friendly recipes
            high_protein: Filter for high-protein recipes
            meal_prep: Filter for meal-prep friendly recipes
            limit: Maximum number of recipes to return

        Returns:
            List of matching recipes
        """
        # Get recipe URLs
        recipe_urls = await self.get_recipe_urls(limit=limit * 2)  # Get more for filtering

        # Scrape recipes
        recipes = []
        for url in recipe_urls:
            recipe = await self.scrape_recipe(url)
            if recipe:
                # Apply filters
                if family_friendly and not recipe.is_family_friendly:
                    continue
                if high_protein and not recipe.is_high_protein:
                    continue
                if meal_prep and not recipe.is_meal_prep_friendly:
                    continue

                # Keyword matching
                if keywords:
                    recipe_text = " ".join(
                        [recipe.title, recipe.description or ""]
                        + [i.name for i in recipe.ingredients]
                    ).lower()
                    if not any(kw.lower() in recipe_text for kw in keywords):
                        continue

                recipes.append(recipe)

                if len(recipes) >= limit:
                    break

        return recipes
