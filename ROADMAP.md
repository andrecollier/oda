# Roadmap - Oda Meal Planner

## Current Version: 0.2.0

---

## 🚀 In Progress

### Budget Meal Planning (v0.2.0)
- ✅ Create 4 budget-friendly recipes (~750 kr total)
- ✅ Automated ingredient shopping list
- ✅ Cart management with product removal
- ⚠️ Manual addition of missing products (automation partially working)

---

## 📋 Planned Features

### High Priority

#### 1. Recipe Review & Favorites System
**Priority**: HIGH
**Status**: Planning

**User Story**:
> "Når jeg starter en samtale i prosjektet, må du spørre meg om hvordan middagene var, slik at jeg kan både reviewe de, justere de, og legge de til i Favoritter."

**Features**:
- [ ] Conversation starter: Ask about previous meals
- [ ] Recipe review functionality (1-5 stars, comments)
- [ ] Favorites management system
- [ ] Recipe adjustment capability
- [ ] Persistent storage of reviews and favorites in database

**Implementation Notes**:
- Add `favorites` table to SQLite database
- Add `recipe_reviews` table with rating and notes
- Create CLI prompts for review collection
- Store meal history with dates

---

#### 2. Enhanced Recipe Information
**Priority**: HIGH
**Status**: Planning

**Missing Features** (from previous version):
- [ ] **Protein content per meal**: Display grams of protein per portion
- [ ] **Nutritional information**: Calories, carbs, fat, protein
- [ ] **Suggested sides**: Salad, bread, vegetables
- [ ] **Drink pairings**: Wine, beer, juice suggestions

**Implementation**:
- Scrape or calculate nutritional data
- Create `NutritionalInfo` model
- Add suggestions database for sides and drinks
- Display in recipe output

---

#### 3. Browser Automation Improvements
**Priority**: HIGH
**Status**: Planning

**Issues**:
- [ ] **Remove cookie popup from preview**: Auto-dismiss cookie consent dialogs
- [ ] **Improve product addition success rate**: Current automation fails on some products
- [ ] **Better selector strategy**: More robust HTML element detection

**Implementation**:
- Add cookie consent handler in Playwright setup
- Research Oda.no's current DOM structure
- Create fallback strategies for product addition
- Log failed product searches for analysis

**Memory/Context to Save**:
```python
# Cookie popup handler approach:
async def dismiss_cookie_popup(page):
    """Dismiss Oda.no cookie consent popup."""
    try:
        # Wait for cookie popup
        cookie_button = await page.wait_for_selector(
            'button:has-text("Godkjenn alle"), button:has-text("Aksepter")',
            timeout=5000
        )
        if cookie_button:
            await cookie_button.click()
            await page.wait_for_timeout(500)
    except:
        pass  # No popup or already dismissed
```

---

#### 4. Purchase History Analysis & Smart Restocking
**Priority**: HIGH
**Status**: Planning

**User Story**:
> "På https://oda.com/no/account/orders/ ser du historikk over alle bestillinger tilbake til 2017. Jeg ønsker at vi lager en ny funksjon hvor du først analyserer alle bestillingene - finner ut hva vi kjøper fast, som melk, pålegg, brød, tannkrem, såpe, etc."

**Features**:
- [ ] **Order History Scraper**: Fetch all orders from 2017-present
- [ ] **Purchase Pattern Analysis**:
  - Identify recurring products (weekly/monthly frequency)
  - Calculate average consumption rate
  - Detect seasonal patterns
- [ ] **"Faste Varer" (Staples) Category**:
  - Auto-suggest staple items based on history
  - One-click add all staples to cart
  - Customize staples list
- [ ] **Smart Restock Suggestions**:
  - Predict when items run out based on:
    - Purchase frequency
    - Product shelf life (milk, bread, etc.)
    - Family size (2 adults + 2 kids)
    - Typical consumption patterns
  - Proactive notifications: "You usually buy milk every 5 days. Last purchase was 4 days ago."

**Implementation Plan**:

1. **Order History Scraper** (`src/oda/order_history.py`):
```python
class OdaOrderHistoryScraper:
    async def fetch_all_orders(self) -> list[Order]:
        """Scrape all orders from account/orders page."""

    async def extract_order_details(self, order_url: str) -> Order:
        """Get detailed product list from single order."""
```

2. **Purchase Analysis Engine** (`src/analysis/purchase_patterns.py`):
```python
class PurchaseAnalyzer:
    def analyze_recurring_items(self, orders: list[Order]) -> list[RecurringItem]
    def calculate_consumption_rate(self, product: str) -> ConsumptionRate
    def predict_restock_date(self, product: str) -> date
```

3. **Staples Manager** (`src/staples.py`):
```python
class StaplesManager:
    def get_suggested_staples(self) -> list[Product]
    def add_to_staples(self, products: list[Product])
    def add_all_staples_to_cart(self)
```

4. **Database Schema**:
```sql
CREATE TABLE order_history (
    id INTEGER PRIMARY KEY,
    order_date DATE,
    order_url TEXT,
    total_price REAL
);

CREATE TABLE order_products (
    id INTEGER PRIMARY KEY,
    order_id INTEGER,
    product_name TEXT,
    quantity INTEGER,
    price REAL,
    FOREIGN KEY (order_id) REFERENCES order_history(id)
);

CREATE TABLE staples (
    id INTEGER PRIMARY KEY,
    product_name TEXT,
    category TEXT,  -- dairy, bread, cleaning, etc.
    avg_frequency_days INTEGER,
    last_purchased DATE,
    is_active BOOLEAN DEFAULT 1
);
```

**Research Needed**:
- Typical shelf life of common groceries
- Consumption rates for family of 4 (2 adults, 2 children)
- Oda.no order history page structure

---

### Medium Priority

#### 5. Price Comparison & Deal Finder
**Status**: Framework exists, needs implementation

- [ ] Weekly deals scraper (`src/oda/deals.py`)
- [ ] Price history tracking
- [ ] Automatic deal notifications
- [ ] Alternative product suggestions (cheaper options)

---

#### 6. Meal Planning Optimization
**Status**: Planning

- [ ] Vegetable reuse across meals (reduce waste)
- [ ] Balanced nutrition across week
- [ ] Variety prevention (don't repeat same proteins)
- [ ] Seasonal ingredient recommendations

---

#### 7. Advanced Shopping Features
**Status**: Planning

- [ ] Out-of-stock product substitution
- [ ] Automatic cart optimization (bundle discounts)
- [ ] Delivery slot booking automation
- [ ] Price alerts for favorite products

---

### Low Priority

#### 8. User Interface
**Status**: Future

- [ ] Web UI (Django/FastAPI)
- [ ] Mobile app integration
- [ ] Email/SMS notifications
- [ ] Calendar integration for meal planning

---

#### 9. Social Features
**Status**: Future

- [ ] Share recipes with friends
- [ ] Community recipe ratings
- [ ] Meal plan templates
- [ ] Collaborative shopping lists

---

## 🐛 Known Issues

### Critical
- [ ] Product addition automation fails ~80% of the time
  - **Root cause**: Oda.no's dynamic HTML structure makes "Legg til" buttons hard to find
  - **Workaround**: Manual addition via browser
  - **Fix**: Need better selector strategy (see Priority #3)

### Major
- [ ] Recipe scraping returns empty ingredients
  - **Root cause**: Oda.no changed recipe page HTML structure
  - **Workaround**: Use simplified recipes with manual ingredients
  - **Fix**: Update selectors in `src/oda/recipes.py`

### Minor
- [ ] Some searches match wrong products (e.g., "gulrot" → "knekkebrød")
  - **Workaround**: More specific search terms
  - **Fix**: Better product name matching algorithm

---

## 📊 Metrics & Goals

### v0.3.0 Goals
- [ ] 95%+ product addition success rate
- [ ] Complete nutritional information for all recipes
- [ ] Favorites system with at least 10 tested recipes
- [ ] Purchase history analysis for last 2 years

### v0.4.0 Goals
- [ ] Automatic weekly meal planning
- [ ] Smart restock suggestions with 90%+ accuracy
- [ ] Price tracking and deal alerts

### v1.0.0 Goals
- [ ] Fully automated weekly grocery shopping
- [ ] Web UI for meal planning
- [ ] Integration with calendar and reminders
- [ ] Community recipe sharing

---

## 💡 Ideas & Suggestions

- **Meal prep mode**: Recipes optimized for batch cooking and freezing
- **Leftover management**: Track what's in fridge, suggest recipes
- **Dietary restrictions**: Filter by allergies, preferences (already partially implemented)
- **Budget tracking**: Weekly/monthly grocery spending analytics
- **Recipe scaling**: Adjust portions automatically
- **Shopping list sharing**: Family members can add items via app

---

## 🔄 Versioning Strategy

- **0.x.x**: Alpha - Core features, breaking changes expected
- **1.x.x**: Beta - Stable API, major features complete
- **2.x.x**: Production - Full automation, web UI, mobile app

---

Last updated: 2026-01-05
