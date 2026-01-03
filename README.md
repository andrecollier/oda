# Oda Meal Planner

Smart meal planning and grocery shopping tool for Oda.no using Claude Code.

## Features

### Core Features
- **Recipe Discovery**: Search Oda.no for family-friendly, high-protein, meal-prep, **quick & easy** recipes
- **Smart Meal Planning**: Optimize weekly meal plans to maximize ingredient reuse (especially vegetables)
- **Product Search**: Search for products with filtering by price, nutrition, allergens
- **Deal Finder**: Automatically find products on sale
- **Shopping List**: Generate consolidated shopping lists from meal plans
- **Cart Management**: Add products to Oda.no cart with checkout guardrail

### NEW! Favorites & History
- **Save Favorites**: Mark recipes you love to easily find them again
- **Rate & Review**: Give recipes 1-5 stars and add personal notes
- **Recipe History**: See what you've made recently
- **Popular Recipes**: Track your most frequently used recipes
- **Search Favorites**: Filter by favorites only when meal planning

### NEW! Visual Preview
- **Cart Preview**: Open browser to visually see your Oda shopping cart
- **Recipe Browser**: Browse Oda recipes with images and filters
- **Recipe Details**: View individual recipes with full details and images

## Architecture

### Data Sources
- **Kassal.app API**: Product search, prices, nutrition info (no scraping needed!)
- **Oda.no (Playwright)**: Recipe scraping and cart management (browser automation)

### Components
- `src/kassal/`: Kassal.app API client
- `src/oda/`: Oda.no recipe scraper and cart manager
- `src/database/`: SQLite database for storing recipes and meal plans
- `src/optimizer/`: Meal plan optimizer (ingredient reuse, nutrition goals)
- `server.py`: MCP server for Claude Code integration

## Setup

### 1. Install Dependencies

```bash
cd oda-meal-planner
python -m pip install -e .
playwright install chromium
```

### 2. Get Kassal.app API Key

1. Go to https://kassal.app/
2. Create an account
3. Navigate to API section
4. Click "Opprett API Nøkkel"
5. Copy your API key

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your credentials
```

Required settings in `.env`:
```
KASSAL_API_KEY=your_api_key_here
ODA_EMAIL=your_oda_email@example.com
ODA_PASSWORD=your_oda_password
HEADLESS_BROWSER=false  # Set to true to hide browser
```

### 4. Start MCP Server

```bash
python server.py
```

## Usage with Claude Code

Once the server is running, you can use natural language with Claude Code:

### Example Conversations

**Find recipes:**
```
"Finn 5 barnevennlige oppskrifter med kylling som er instant-pot vennlige"
```

**Search for deals:**
```
"Hva er på tilbud i kategorien grønnsaker?"
```

**Create meal plan:**
```
"Lag en ukeplan for 5 middager som gjenbruker brokkoli og paprika,
med høyt proteininnhold for voksne"
```

**Generate shopping list:**
```
"Generer handlekurv basert på ukesplanen"
```

**Add to cart:**
```
"Legg alt i handlekurven på Oda"
```

**Checkout (with guardrail):**
```
"Forbered checkout"
```
→ Browser will open to checkout page, but you must complete purchase manually

**Visual Preview (NEW!):**
```
"Åpne handlekurven min i nettleseren så jeg kan se produktene visuelt"
"Vis meg Oda oppskrifter i nettleseren"
"Åpne denne oppskriften i browseren: https://oda.com/no/recipes/123-kylling-med-ris"
```
→ Browser opens with Playwright Inspector - you can browse visually and click "Resume" when done

## Available Tools

The MCP server exposes these tools to Claude Code:

### Product & Deal Discovery
- `search_products`: Search for products with filters
- `find_deals`: Find products on sale
- `find_high_protein_products`: Find high-protein items

### Recipe Management
- `search_recipes`: Search Oda.no recipes with filters (family-friendly, quick & easy, high-protein, meal prep)
- `get_favorites`: View your favorite recipes
- `get_recipe_history`: See recently used recipes
- `get_popular_recipes`: See most frequently used recipes
- `mark_favorite`: Add/remove recipes from favorites
- `rate_recipe`: Rate recipes 1-5 stars and add notes
- `create_meal_plan`: Create optimized weekly meal plan
- `get_meal_plan`: View current meal plan
- `analyze_meal_plan`: Analyze ingredient reuse

### Shopping
- `generate_shopping_list`: Create shopping list from meal plan
- `add_to_cart`: Add items to Oda cart
- `view_cart`: View cart contents
- `checkout_guardrail`: Prepare checkout (manual completion required)

### Visual Preview (NEW!)
- `preview_cart`: Open browser to visually see your shopping cart with all products and prices
- `preview_recipes`: Open browser to browse Oda.no recipes page visually with filters
- `preview_recipe`: Open browser to view a specific recipe with images and ingredients

## Optimization Features

### Ingredient Reuse
The optimizer maximizes reuse of vegetables across meals:
- Prioritizes recipes that share vegetables
- Reduces waste and shopping complexity
- Calculates reuse ratio for transparency

### Nutritional Goals
- Target protein per meal (default: 30g for adults)
- Filter for family-friendly recipes
- Support for meal prep / batch cooking

### Smart Shopping
- Consolidates ingredients across recipes
- Groups by category
- Shows which ingredients are used in multiple meals
- Finds best prices via Kassal.app

## Database

SQLite database stores:
- Scraped recipes (cached for speed)
- Weekly meal plans
- Shopping lists
- Saved deals

Location: `data/meal_planner.db`

## Guardrails

### Checkout Guardrail
The system **never** completes checkout automatically. The `checkout_guardrail` tool:
1. Navigates to checkout page
2. Shows cart summary and total price
3. **STOPS** - you must manually complete purchase in browser

This prevents accidental purchases.

## Configuration

Edit `.env` to customize:

```env
# Meal planning preferences
DEFAULT_MEAL_DAYS=5              # Number of days to plan
PROTEIN_GOAL_PER_MEAL=30         # Grams of protein target
CHILD_FRIENDLY_MODE=true         # Prefer family recipes
MEAL_PREP_MODE=true              # Prefer meal-prep friendly

# Browser
HEADLESS_BROWSER=false           # Show/hide browser
```

## Troubleshooting

### "Login failed"
- Check Oda credentials in `.env`
- Try with `HEADLESS_BROWSER=false` to see what's happening

### "403 Forbidden" from Kassal.app
- Verify API key is correct
- Check rate limits (60 requests/minute)

### Recipes not found
- Ensure you're logged into Oda.no
- Try different search keywords
- Some recipes may have changed on Oda.no

## Development

### Run tests
```bash
pytest
```

### Code quality
```bash
ruff check src/
```

## Privacy & Security

- All data stored locally (SQLite)
- API keys in `.env` (not committed to git)
- Oda credentials used only for authentication
- No data shared with third parties

## Credits

- **Kassal.app**: Product data API
- **Oda.no**: Recipes and shopping
- **Playwright**: Browser automation
- **Claude Code**: AI-powered meal planning

## License

MIT
