# Quick Start Guide

Get started with Oda Meal Planner in 5 minutes!

## 1. Get Kassal.app API Key (2 min)

1. Visit https://kassal.app/
2. Sign up for a free account
3. Navigate to the API section
4. Click "Opprett API Nøkkel" (Create API Key)
5. Copy your API key

## 2. Run Setup Script (2 min)

```bash
cd oda-meal-planner
./setup.sh
```

This will:
- Create Python virtual environment
- Install all dependencies
- Install Playwright browsers
- Create data directory

## 3. Configure Credentials (1 min)

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:
```env
KASSAL_API_KEY=your_kassal_api_key_here
ODA_EMAIL=your_oda_email@example.com
ODA_PASSWORD=your_oda_password
```

**Optional settings:**
```env
HEADLESS_BROWSER=false          # Set to true to hide browser
DEFAULT_MEAL_DAYS=5             # Number of days to plan
PROTEIN_GOAL_PER_MEAL=30        # Protein target (grams)
CHILD_FRIENDLY_MODE=true        # Prefer family-friendly recipes
MEAL_PREP_MODE=true             # Prefer meal-prep friendly
```

## 4. Start the Server

```bash
source .venv/bin/activate
python server.py
```

You should see:
```
MCP Server running...
```

## 5. Use with Claude Code

Now you can use natural language to interact with the system!

### Example 1: Find Recipes
```
"Finn 3 barnevennlige oppskrifter med kylling"
```

Claude Code will:
1. Call `search_recipes` tool
2. Scrape Oda.no for recipes
3. Filter for family-friendly chicken recipes
4. Save to database
5. Show you the results

### Example 2: Create Weekly Meal Plan
```
"Lag en ukeplan for 5 middager som bruker brokkoli og paprika,
med høyt protein for voksne"
```

Claude Code will:
1. Search for recipes with those ingredients
2. Filter for high-protein recipes
3. Run optimizer to maximize vegetable reuse
4. Create meal plan in database
5. Show analysis of ingredient overlap

### Example 3: Generate Shopping List & Add to Cart
```
"Generer handlekurv og legg alt i Oda-handlekurven"
```

Claude Code will:
1. Generate shopping list from meal plan
2. Consolidate ingredients by category
3. Open browser (if not headless)
4. Log into Oda.no
5. Add each item to cart
6. Show summary

### Example 4: Checkout (with Guardrail)
```
"Forbered checkout"
```

Claude Code will:
1. Navigate to checkout page
2. Show cart summary and total price
3. **STOP** (you must complete purchase manually in browser)

## Tips

### See What's Happening
Set `HEADLESS_BROWSER=false` in `.env` to watch the browser automation.

### Find Deals
```
"Hva er på tilbud i kategorien kjøtt?"
```

### High Protein Search
```
"Finn høyprotein produkter med over 20g protein per 100g"
```

### Analyze Meal Plan
```
"Analyser ukesplanen min - hvor mye gjenbruker vi grønnsaker?"
```

## Common Issues

**"Login failed"**
- Check Oda credentials in `.env`
- Make sure account is active
- Try with `HEADLESS_BROWSER=false` to see login page

**"403 Forbidden" from Kassal**
- Check API key is correct
- Verify you haven't hit rate limit (60/min)

**"No recipes found"**
- Try broader search terms
- Remove some filters
- Check Oda.no still has recipes page

## Next Steps

Once you're comfortable with basic usage:

1. **Customize preferences**: Edit `.env` to match your family's needs
2. **Explore all tools**: See README.md for full tool list
3. **Build workflows**: Combine tools for complex meal planning
4. **Optimize**: Analyze ingredient reuse to reduce waste

## Example Workflows

### Complete Weekly Planning
```
1. "Finn 8 barnevennlige middager med variasjon"
2. "Lag ukeplan for 5 middager, optimalisert for gjenbruk av grønnsaker"
3. "Generer handlekurv"
4. "Legg alt i Oda-handlekurven"
5. "Forbered checkout"
```

### Deal Hunting
```
1. "Finn tilbud på kjøtt og fisk"
2. "Finn oppskrifter som bruker produkter på tilbud"
3. "Lag ukeplan basert på tilbudsoppskrifter"
```

### Protein-Focused
```
1. "Finn høyprotein oppskrifter over 30g protein per porsjon"
2. "Lag ukeplan for 5 middager med minst 35g protein"
3. "Generer handlekurv med fokus på proteinkilder"
```

## Support

- **Issues**: Check README.md troubleshooting section
- **Questions**: Review tool documentation in README.md
- **Bugs**: File an issue or check logs

Enjoy smart meal planning! 🍽️
