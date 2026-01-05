# Changelog

All notable changes to the Oda Meal Planner project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-01-05

### Added
- **Budget meal planning**: Created 4 budget-friendly recipes (~750 kr total, ~47 kr/portion)
  - Spaghetti Bolognese (30 min, ~180 kr)
  - Chili sin carne - vegetarian (35 min, ~120 kr)
  - Kjøttboller med pasta (40 min, ~180 kr)
  - Pølse- og potetgryte (45 min, ~150 kr)
- **Recipe finder script** (`find_oda_recipes.py`): Automated recipe search from Oda.no with filters
  - Family-friendly filter
  - Quick & easy filter
  - High-protein filter
  - Meal prep filter
- **Budget replacement finder** (`find_budget_replacements.py`): Find cheap alternative recipes
- **Cart management improvements**:
  - `clear_cart_completely.py`: Remove all products from cart
  - `final_cleanup.py`: Remove wrong products and add correct ones
  - `add_missing_budget_ingredients.py`: Add missing ingredients for budget meals
- **Enhanced cart manager** (`src/oda/cart.py`):
  - `search_products()`: Search and return multiple product results with prices
  - Better price extraction using regex
  - Improved product matching logic
- **Deals manager** (`src/oda/deals.py`): Framework for scraping weekly deals from Oda.no
- **New data models** (`src/oda/models.py`):
  - `Deal`: Represents weekly deals/discounts
  - `ProductAlternative`: Alternative products for an ingredient
- **.gitignore improvements**: Filter out debug files, screenshots, and temporary data

### Changed
- **Recipe scraper** (`src/oda/recipes.py`): Improved ingredient extraction from accordion tables
- **Cart workflow**: Now clears old cart before adding new products
- **Budget focus**: Shifted from expensive recipes to budget-friendly alternatives

### Fixed
- Cart removal functionality using aria-label for button detection
- Product search matching for specific items (avoiding økologisk, pre-cut variants)
- Lactose-free requirement enforced for dairy products

### Documentation
- Created comprehensive recipe document with all 4 budget meals
- Included shopping list, weekly menu suggestions, and money-saving tips
- Added batch cooking recommendations

## [0.1.0] - 2026-01-03

### Added
- Initial project setup
- Oda.no authentication and login system
- Basic recipe scraper using Playwright
- Cart management functionality
- Product search and add to cart
- Environment configuration with Pydantic
- MCP server integration (19 tools available)

### Features
- Recipe search with filters (family-friendly, quick & easy, high-protein, meal prep)
- Shopping cart integration with Oda.no
- Product search via Kassal.app API integration
- SQLite database for persistent storage
- Playwright-based browser automation

### Technical
- Python 3.10+ support
- Async/await pattern throughout
- Type-safe data models with Pydantic
- Comprehensive error handling
