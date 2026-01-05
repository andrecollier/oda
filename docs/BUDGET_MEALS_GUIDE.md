# Budget Meals Guide

## Quick Start

Get 4 complete dinners for ~750 kr (~47 kr/portion):

```bash
# 1. Find budget recipes
python find_budget_replacements.py

# 2. Add missing ingredients to cart
python add_missing_budget_ingredients.py

# 3. View recipes
cat "Oppskrifter/Uke 1 - 2026/OPPSKRIFTER - 4 BUDSJETT MIDDAGER - Uke 1.txt"
```

## The 4 Budget Dinners

### 1. Spaghetti Bolognese
**Cost**: ~180 kr | **Time**: 30 min | **Portions**: 4

Classic pasta with meat sauce. Perfect for batch cooking - make double and freeze half.

**Key Ingredients**:
- 400g kjøttdeig
- 400g pasta
- 400g hakkede tomater (hermetikk)
- Løk, hvitløk, buljong

**Pro Tip**: Add milk for a creamier sauce, or gratiner with cheese on top.

---

### 2. Chili sin Carne (Vegetarian)
**Cost**: ~120 kr | **Time**: 35 min | **Portions**: 4

Budget-friendly vegetarian chili with beans. The cheapest of the 4 meals!

**Key Ingredients**:
- 400g hakkede tomater (hermetikk)
- 400g kidney beans (hermetikk)
- Taco krydder
- Ris
- Løk, hvitløk, buljong

**Pro Tip**: Serve with sour cream (lactose-free), nachos, or tortillas. Great for meal prep!

---

### 3. Kjøttboller med Pasta
**Cost**: ~180 kr | **Time**: 40 min | **Portions**: 4

Homemade meatballs in creamy tomato sauce. Kids love this!

**Key Ingredients**:
- 400g kjøttdeig
- 1 egg
- 400g pasta
- 400g hakkede tomater
- Kremfløte laktosefri
- Løk, hvitløk, buljong

**Pro Tip**: Make double portion of meatballs and freeze. Use havregryn instead of breadcrumbs.

---

### 4. Pølse- og Potetgryte
**Cost**: ~150 kr | **Time**: 45 min | **Portions**: 4

Hearty one-pot stew with sausages and potatoes. Perfect for cold winter nights.

**Key Ingredients**:
- 1 pakke pølser (6-8 stk)
- 800g poteter
- 2 gulrøtter
- 400g hakkede tomater
- Melk lett
- Løk, hvitløk, buljong

**Pro Tip**: Use leftover breakfast sausages. Add mais or peas for variation.

---

## Shopping Strategy

### Already in Cart (~598 kr)
✅ Kjøttdeig x2
✅ Pølser
✅ Pasta x2
✅ Melk lett
✅ Kremfløte laktosefri
✅ Løk
✅ Hvitløk
✅ Poteter

### Need to Add (~150 kr)
❌ Hakkede tomater x2 (hermetikk) - ~30 kr
❌ Kidney beans x1 (hermetikk) - ~16 kr
❌ Ris (jasmin eller annen billig) - ~30 kr
❌ Taco krydder - ~20 kr
❌ Buljongterninger x2-3 - ~20 kr
❌ Gulrøtter (pose) - ~20 kr
❌ Egg x1 (if don't have) - ~15 kr

**Total**: ~750 kr for 16 portions = ~47 kr/portion ✅

---

## Money-Saving Tips

### 1. Choose Cheapest Brands
- ❌ AVOID: Økologisk products (2x more expensive)
- ❌ AVOID: Pre-cut vegetables (ferdig kuttet)
- ✅ CHOOSE: Store brands (Oda, First Price)
- ✅ CHOOSE: Canned/hermetikk (cheaper than fresh)

### 2. Batch Cooking
- Make **2x portions** of Bolognese and Chili
- Freeze half in meal-sized containers
- Saves time AND money (fewer shopping trips)

### 3. Ingredient Reuse
- Løk and hvitløk used in **ALL 4 recipes**
- Hakkede tomater in **3 of 4 recipes**
- Pasta in **2 recipes**
- No waste!

### 4. Smart Substitutions
- No breadcrumbs? Use **havregryn** (oats)
- No egg? Add extra buljong for binding
- No spices? Use **salt, pepper, and bouillon**

### 5. Portion Control
- All recipes serve **4 people**
- Perfect for family of 3-4
- Or 2 adults with leftovers for lunch

---

## Weekly Menu Plan

**MONDAY**: Spaghetti Bolognese (quick weeknight meal)
**TUESDAY**: Chili sin Carne (vegetarian, quick)
**WEDNESDAY**: Kjøttboller med Pasta (comfort food)
**THURSDAY**: Pølse- og Potetgryte (use up leftovers)

**FRIDAY**: Frozen Bolognese or Chili from batch cooking
**WEEKEND**: Takeout/pizza from remaining budget

---

## Troubleshooting

### Products Not Found in Cart Automation?
**Solution**: Add manually in browser:
1. Search for "hakkede tomater hermetikk"
2. Choose **billigste** (cheapest) option
3. Click "Legg til"
4. Repeat for all 6 missing items

### Cart Total Over 750 kr?
**Causes**:
- Selected økologisk products (too expensive)
- Selected ferdig kuttet (pre-cut, more expensive)
- Added extras not in recipe

**Solution**: Run `final_cleanup.py` to remove expensive items

### Missing Nutritional Info?
**Status**: Coming in v0.3.0
- Protein content per meal
- Calorie counts
- Suggested sides and drinks

---

## Advanced Features (Coming Soon)

### Recipe Review & Favorites
- Rate meals after cooking
- Mark favorites for easy access
- Track meal history

### Purchase History Analysis
- Analyze past Oda orders (back to 2017)
- Identify staple items (milk, bread, etc.)
- Auto-suggest restocking schedule
- Predict when items run out

### Smart Recommendations
- Protein content per meal
- Suggested side dishes
- Drink pairings
- Leftover management

---

## Scripts Reference

### Core Scripts

**`find_oda_recipes.py`**
Find recipes from Oda.no with filters:
- Family-friendly
- Quick & easy
- High-protein
- Meal prep

**`find_budget_replacements.py`**
Find budget-friendly recipe alternatives:
- Under 12 ingredients
- No expensive proteins (torsk, laks, entrecôte)
- Uses cart ingredients

**`add_missing_budget_ingredients.py`**
Add missing ingredients to cart:
- Automated search and add
- Fallback to manual if automation fails
- Avoids økologisk and ferdig kuttet

**`clear_cart_completely.py`**
Remove all products from cart:
- Clean slate for new meal plan
- Uses aria-label for reliable removal
- Handles 50+ products

**`final_cleanup.py`**
Smart cart cleanup:
- Remove wrong products (økologisk, utsolgt, etc.)
- Add correct budget alternatives
- Verify total price

---

## Budget Breakdown

```
FIXED COSTS (already in cart):
├── Proteins (213 kr)
│   ├── Kjøttdeig x2: 130 kr
│   └── Pølser: 83 kr
├── Carbs (110 kr)
│   └── Pasta x2: 80 kr
│   └── Poteter: 35 kr (also used in gryte)
├── Dairy (66 kr)
│   ├── Melk lett: 36 kr
│   └── Kremfløte laktosefri: 30 kr
├── Aromatics (35 kr)
│   ├── Løk: 17 kr
│   └── Hvitløk: 18 kr
└── SUBTOTAL: 598 kr

MISSING ITEMS (~152 kr):
├── Canned goods (46 kr)
│   ├── Hakkede tomater x2: 30 kr
│   └── Kidney beans: 16 kr
├── Pantry staples (70 kr)
│   ├── Ris: 30 kr
│   ├── Taco krydder: 20 kr
│   └── Buljong x3: 20 kr
├── Fresh produce (20 kr)
│   └── Gulrøtter (pose): 20 kr
└── Optional (15 kr)
    └── Egg: 15 kr

GRAND TOTAL: ~750 kr
```

**Per Portion Cost**: 750 kr / 16 portions = **46.88 kr/portion** ✅

Compare to:
- Takeout pizza: ~150-200 kr/person
- Restaurant meal: ~250-400 kr/person
- Pre-made meals: ~80-120 kr/portion

**Savings**: ~60-80% compared to eating out!

---

## Lactose-Free Compliance ✅

All dairy products are **lactose-free** as required:
- ✅ Melk lett (lactose-free milk)
- ✅ Kremfløte laktosefri (lactose-free cream)

**Note**: Double-check product labels when shopping manually.

---

Last updated: 2026-01-05
