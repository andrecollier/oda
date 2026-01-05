# 🔧 Oda Meal Planner - Teknisk Dokumentasjon

## Arkitektur oversikt

```
oda-meal-planner/
├── src/
│   ├── config.py              # Konfigurasjon (env vars)
│   ├── database/              # Database models & operations
│   │   ├── models.py          # SQLAlchemy models
│   │   └── db.py              # Database operations
│   ├── kassal/                # Kassal.app API integration
│   │   └── client.py          # Product search & pricing
│   ├── oda/                   # Oda.no scrapers
│   │   ├── recipes.py         # Recipe scraper
│   │   ├── cart.py            # Shopping cart manager
│   │   ├── orders.py          # Order history scraper
│   │   └── models.py          # Pydantic models
│   └── optimizer/             # Meal planning optimization
│       └── meal_optimizer.py  # Ingredient reuse optimizer
├── server.py                  # MCP server (main entry point)
└── data/
    └── meal_planner.db        # SQLite database
```

---

## Database Schema

### Tables

#### `recipes`
Lagrer oppskrifter fra Oda.no
```sql
- id: str (PK)
- title: str
- url: str
- servings: int
- cooking_time: str
- protein_per_serving: float
- ingredients: JSON
- instructions: JSON
- is_favorite: bool
- rating: int (1-5)
- times_used: int
- last_used: datetime
```

#### `meal_plans`
Ukentlige middagsplaner
```sql
- id: int (PK)
- recipe_id: str (FK -> recipes.id)
- day_of_week: int (0=Monday)
- week_number: int (ISO week)
- year: int
- servings: int
```

#### `shopping_list`
Handleliste for uken
```sql
- id: int (PK)
- name: str
- quantity: str
- category: str
- oda_product_url: str
- week_number: int
- year: int
- purchased: bool
```

#### `orders`
Historiske bestillinger fra Oda
```sql
- id: int (PK)
- order_number: str (UNIQUE)
- order_date: datetime
- total_price: float
- status: str
```

#### `order_items`
Produkter i bestillinger
```sql
- id: int (PK)
- order_id: int (FK -> orders.id)
- product_name: str
- quantity: int
- price_per_unit: float
- category: str
```

#### `recurring_items`
Faste varer (analysert fra order history)
```sql
- id: int (PK)
- product_name: str (UNIQUE)
- purchase_count: int
- first_purchase: datetime
- last_purchase: datetime
- avg_days_between_purchase: float
- typical_quantity: int
- estimated_days_supply: int
- next_predicted_purchase: datetime
- is_low_stock_warning: bool
- auto_add_to_list: bool
```

---

## Scrapers

### OdaRecipeScraper

**Technology:** Playwright (Chromium)

**Methods:**
- `login()` - Login til Oda.no
- `search_recipes(keywords, filters)` - Søk oppskrifter
- `scrape_recipe(url)` - Scrape enkelt oppskrift
- `preview_recipe(url)` - Åpne oppskrift i browser
- `_dismiss_cookie_popup()` - Fjern cookie popup

**Selectors brukt:**
```python
# Login
'#email-input'
'#password-input'
'button[type="submit"]'

# Recipes
'a[href*="/recipes/"]'
'[data-test-id="accordion-ingredients"]'
'[class*="instructionContainer"]'
```

### OdaCartManager

**Technology:** Playwright (Chromium)

**Methods:**
- `add_product_by_search(name, quantity)` - Søk og legg til produkt
- `add_product_by_url(url, quantity)` - Legg til via URL
- `search_products(name, limit)` - Søk produkter (returnerer liste)
- `get_cart_items()` - Hent innhold i handlekurv
- `preview_cart()` - Åpne handlekurv i browser
- `_dismiss_cookie_popup()` - Fjern cookie popup

**Smart product selection:**
```python
# Foretrekker bulk products
prefer_keywords = ["pose", "løsvekt", "kg", "hel"]

# Unngår pre-cut/expensive
avoid_keywords = ["staver", "kuttet", "ferdig", "mini"]
```

### OdaOrderScraper

**Technology:** Playwright (Chromium)

**Methods:**
- `scrape_orders(max_orders)` - Scrape order history
- `_scrape_order_detail(url)` - Scrape items fra order detail

**URL:** `https://oda.com/no/account/orders/`

**Parsing strategy:**
- Scroll for å laste flere orders
- Extract order number via regex: `(?:Ordre|Order)\s*#?(\d+)`
- Extract date: `(\d{1,2})[.\s]+([a-zæøå]+)[.\s]+(\d{4})`
- Click order for å få items
- Parse product names og quantities

---

## Recurring Items Analysis

### Algorithm

```python
def analyze_recurring_items(min_purchases=3):
    1. Hent alle order_items fra database
    2. Gruppe etter product_name (normalized/lowercase)
    3. For hver product med >= min_purchases:
        a. Sorter purchases etter dato
        b. Beregn avg_days_between_purchase
        c. Beregn typical_quantity (gjennomsnitt)
        d. Estimer days_supply basert på produkttype
        e. Prediker next_purchase_date
        f. Sett is_low_stock hvis < 3 dager til next purchase
    4. Lagre til recurring_items tabell
```

### Product Lifespan Estimation

```python
# Fresh products (short lifespan)
if "melk" or "brød" in name:
    return min(7, avg_days_between)

# Dairy (medium lifespan)
if "yoghurt" or "ost" in name:
    return min(14, avg_days_between)

# Household (long lifespan)
if "såpe" or "tannkrem" in name:
    return int(avg_days_between * 0.9)

# Default
return int(avg_days_between)
```

### Prediction Formula

```
next_purchase = last_purchase + avg_days_between_purchase
days_until_empty = (next_purchase - today).days
is_low_stock = days_until_empty <= 3
```

---

## MCP Server Tools

### Recipe Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `search_recipes` | Søk oppskrifter | keywords, filters, limit |
| `get_favorites` | Hent favoritter | limit |
| `mark_favorite` | Marker favoritt | recipe_id, is_favorite |
| `rate_recipe` | Gi rating | recipe_id, rating, notes |
| `preview_recipe` | Vis i browser | recipe_url |

### Meal Planning Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `create_meal_plan` | Lag ukesplan | recipe_ids, num_days, optimize |
| `get_meal_plan` | Hent gjeldende plan | - |
| `generate_shopping_list` | Generer handleliste | - |
| `analyze_meal_plan` | Analyser ingredient overlap | - |

### Shopping Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `search_products` | Søk produkter (Kassal API) | search, category, price_max |
| `find_deals` | Finn tilbud | category, min_discount |
| `add_to_cart` | Legg til i Oda-kurv | items (name/url + quantity) |
| `view_cart` | Se handlekurv | - |
| `preview_cart` | Åpne i browser | - |

### Recurring Items Tools (NEW!)

| Tool | Description | Parameters |
|------|-------------|------------|
| `scrape_order_history` | Scrape bestillingshistorikk | max_orders |
| `analyze_recurring_items` | Analyser faste varer | min_purchases |
| `get_recurring_items` | Liste faste varer | limit |
| `get_low_stock_warnings` | Få low-stock varsler | - |
| `add_recurring_to_shopping_list` | Legg til i liste | low_stock_only, product_names |

---

## Smart Features

### Cookie Popup Removal

**Implementert i:**
- `OdaCartManager._dismiss_cookie_popup()`
- `OdaRecipeScraper._dismiss_cookie_popup()`
- `OdaOrderScraper._dismiss_cookie_popup()`

**Selectors testet:**
```python
[
    'button:has-text("Godta alle")',
    'button:has-text("Aksepter")',
    'button:has-text("Jeg forstår")',
    '[id*="cookie"] button',
    '[class*="cookie"] button',
]
```

### Intelligent Side & Drink Suggestions

**Implementert i:** `Recipe.suggest_sides_and_drinks()`

**Logic:**
```python
# Detect missing carbs -> suggest carbs
if not has_carbs:
    if "asian" in recipe: suggest ["rice", "noodles"]
    elif "italian" in recipe: suggest ["pasta", "bread"]
    else: suggest ["potatoes", "rice"]

# Detect missing vegetables -> suggest salad
if not has_salad:
    suggest ["green salad", "cucumber salad"]

# Detect dry proteins -> suggest sauces
if "chicken" and not "sauce":
    suggest ["bearnaise", "tzatziki", "aioli"]

# Drinks based on audience
if "family-friendly":
    suggest ["milk", "water", "juice"]
else:
    suggest ["water", "wine (adults)"]
```

### Meal Optimizer

**Implementert i:** `MealOptimizer`

**Optimization goal:** Maksimer gjenbruk av grønnsaker

**Algorithm:**
```python
def optimize_meal_plan(recipes, num_days):
    1. Extract all vegetables from each recipe
    2. Create overlap matrix (hvilke oppskrifter deler grønnsaker)
    3. Greedily select recipes med høyest overlap
    4. Returner optimized plan
```

**Metrics:**
- `vegetable_reuse_ratio`: % av grønnsaker som brukes i flere oppskrifter
- `total_vegetable_items`: Totalt antall grønnsak-items
- `unique_vegetables`: Antall unike grønnsaker

---

## Configuration

### Environment Variables (.env)

```bash
# Oda credentials
ODA_EMAIL=din.email@example.com
ODA_PASSWORD=ditt-passord

# Kassal.app API (for product search)
KASSAL_API_KEY=your-api-key

# Database
DATABASE_URL=sqlite:///./data/meal_planner.db

# Browser settings
HEADLESS_BROWSER=true

# Meal planning preferences
PROTEIN_GOAL_PER_MEAL=30  # grams
CHILD_FRIENDLY_MODE=true
MEAL_PREP_MODE=true
```

---

## Performance Considerations

### Database queries
- Use indexes on frequently queried fields:
  - `recipes.is_favorite`
  - `recipes.last_used`
  - `orders.order_date`
  - `recurring_items.is_low_stock_warning`

### Scraping optimization
- Use `headless=True` for production (2x faster)
- Cache recipe data in database to avoid re-scraping
- Limit order scraping to recent orders (e.g., last 100)

### Memory usage
- Order scraping can be memory-intensive with 100+ orders
- Consider chunking in batches of 50 orders

---

## Error Handling

### Common errors

**Login timeout:**
```python
# Increase timeout in login()
await self.page.wait_for_load_state("networkidle", timeout=30000)
```

**Element not found:**
```python
# Multiple selector fallbacks
for selector in selectors:
    try:
        element = await page.query_selector(selector)
        if element: break
    except: continue
```

**Rate limiting:**
- Add delays between requests: `await page.wait_for_timeout(1000)`
- Respect Oda's servers

---

## Testing

### Unit tests
```bash
# Test database operations
python -m pytest tests/test_database.py

# Test scrapers (requires credentials)
python -m pytest tests/test_scrapers.py
```

### Manual testing
```bash
# Test order scraping
python test_order_scraping.py

# Test MCP server
python server.py
```

---

## Future Enhancements

### Planned features
- [ ] 2FA support for login
- [ ] Price tracking over time
- [ ] Nutritional analysis (carbs, fat, etc.)
- [ ] Recipe recommendations based on history
- [ ] Integration med andre matbutikker
- [ ] Mobile app
- [ ] Voice commands

### Known limitations
- Requires Oda.no account
- Scraping kan bryte hvis Oda endrer HTML
- No 2FA support yet
- Kun norsk språk

---

## Contributing

### Code style
- Python 3.10+
- Type hints everywhere
- Docstrings for all public methods
- Black formatting

### Adding new scrapers
1. Inherit from base scraper class
2. Implement login, scrape, and preview methods
3. Add `_dismiss_cookie_popup()` support
4. Add to MCP server tools

---

## License

Private project - All rights reserved

---

**Maintainer:** André Collier via Claude Code
**Last updated:** January 2025
