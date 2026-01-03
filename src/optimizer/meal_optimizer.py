"""Meal planning optimizer."""

from collections import Counter
from typing import Any
from ..oda.models import Recipe


class MealOptimizer:
    """Optimize meal plans for ingredient reuse and nutritional goals."""

    def __init__(
        self,
        protein_goal_per_meal: float = 30.0,
        prefer_family_friendly: bool = True,
        prefer_meal_prep: bool = True,
    ):
        """Initialize meal optimizer.

        Args:
            protein_goal_per_meal: Target protein per meal in grams
            prefer_family_friendly: Prefer family-friendly recipes
            prefer_meal_prep: Prefer meal-prep friendly recipes
        """
        self.protein_goal = protein_goal_per_meal
        self.prefer_family_friendly = prefer_family_friendly
        self.prefer_meal_prep = prefer_meal_prep

    def score_recipe(self, recipe: Recipe, used_vegetables: set[str]) -> float:
        """Score a recipe based on optimization criteria.

        Higher score is better. Considers:
        - Ingredient reuse (higher score for using vegetables already in plan)
        - Protein content (higher score for meeting protein goal)
        - Family-friendly (bonus if preferred)
        - Meal-prep friendly (bonus if preferred)

        Args:
            recipe: Recipe to score
            used_vegetables: Set of vegetables already used in meal plan

        Returns:
            Score (0-100)
        """
        score = 50.0  # Base score

        # 1. Ingredient reuse bonus (up to +30 points)
        recipe_veggies = set(recipe.main_vegetables)
        if used_vegetables:
            overlap = recipe_veggies & used_vegetables
            reuse_ratio = len(overlap) / len(used_vegetables) if used_vegetables else 0
            score += reuse_ratio * 30

        # 2. Protein content (up to +20 points)
        if recipe.protein_per_serving:
            protein_diff = abs(recipe.protein_per_serving - self.protein_goal)
            protein_score = max(0, 20 - protein_diff)
            score += protein_score

        # 3. Family-friendly bonus (+15 points)
        if self.prefer_family_friendly and recipe.is_family_friendly:
            score += 15

        # 4. Meal-prep bonus (+15 points)
        if self.prefer_meal_prep and recipe.is_meal_prep_friendly:
            score += 15

        # 5. High protein bonus (+10 points)
        if recipe.is_high_protein:
            score += 10

        return min(100, score)

    def optimize_meal_plan(
        self,
        available_recipes: list[Recipe],
        num_meals: int = 5,
    ) -> list[Recipe]:
        """Select optimal recipes for a meal plan.

        Maximizes ingredient reuse while meeting nutritional goals.

        Args:
            available_recipes: List of recipes to choose from
            num_meals: Number of meals to plan

        Returns:
            List of selected recipes (optimized order)
        """
        if not available_recipes:
            return []

        if len(available_recipes) <= num_meals:
            return available_recipes

        selected = []
        used_vegetables: set[str] = set()

        # First, select the highest-scoring recipe overall
        first_recipe = max(available_recipes, key=lambda r: self.score_recipe(r, set()))
        selected.append(first_recipe)
        used_vegetables.update(first_recipe.main_vegetables)
        remaining = [r for r in available_recipes if r.id != first_recipe.id]

        # Then, iteratively select recipes that maximize reuse
        for _ in range(num_meals - 1):
            if not remaining:
                break

            # Score all remaining recipes based on current vegetables
            scored = [
                (recipe, self.score_recipe(recipe, used_vegetables)) for recipe in remaining
            ]

            # Select best recipe
            best_recipe, _ = max(scored, key=lambda x: x[1])
            selected.append(best_recipe)
            used_vegetables.update(best_recipe.main_vegetables)
            remaining = [r for r in remaining if r.id != best_recipe.id]

        return selected

    def analyze_ingredient_overlap(self, recipes: list[Recipe]) -> dict[str, Any]:
        """Analyze ingredient overlap in a set of recipes.

        Args:
            recipes: List of recipes

        Returns:
            Dictionary with overlap statistics
        """
        all_vegetables = []
        all_ingredients = []

        for recipe in recipes:
            all_vegetables.extend(recipe.main_vegetables)
            all_ingredients.extend([ing.name for ing in recipe.ingredients])

        veg_counter = Counter(all_vegetables)
        ing_counter = Counter(all_ingredients)

        # Calculate reuse metrics
        total_veg_items = len(all_vegetables)
        unique_veg = len(veg_counter)
        reuse_ratio = 1 - (unique_veg / total_veg_items) if total_veg_items > 0 else 0

        return {
            "total_recipes": len(recipes),
            "total_vegetable_items": total_veg_items,
            "unique_vegetables": unique_veg,
            "vegetable_reuse_ratio": reuse_ratio,
            "most_common_vegetables": veg_counter.most_common(5),
            "most_common_ingredients": ing_counter.most_common(10),
            "vegetables_by_frequency": dict(veg_counter),
        }

    def generate_shopping_list(
        self, recipes: list[Recipe]
    ) -> dict[str, list[dict[str, str]]]:
        """Generate consolidated shopping list from recipes.

        Groups ingredients by category and consolidates quantities.

        Args:
            recipes: List of recipes

        Returns:
            Dictionary mapping category to list of items
        """
        # Collect all ingredients
        all_ingredients = []
        for recipe in recipes:
            for ing in recipe.ingredients:
                all_ingredients.append(
                    {
                        "name": ing.name,
                        "amount": ing.amount or "",
                        "unit": ing.unit or "",
                        "product_url": ing.product_url,
                    }
                )

        # Group by ingredient name (basic consolidation)
        ingredient_map: dict[str, list[dict]] = {}
        for ing in all_ingredients:
            name = ing["name"].lower().strip()
            if name not in ingredient_map:
                ingredient_map[name] = []
            ingredient_map[name].append(ing)

        # Categorize ingredients
        categories = {
            "Grønnsaker": [
                "brokkoli",
                "gulrot",
                "paprika",
                "løk",
                "tomat",
                "agurk",
                "salat",
                "squash",
            ],
            "Kjøtt & Fisk": ["kylling", "laks", "kjøttdeig", "bacon", "svin", "kalv", "kalkun"],
            "Meieri": ["melk", "ost", "yoghurt", "smør", "fløte", "rømme"],
            "Tørrvarer": ["pasta", "ris", "mel", "havre", "brød"],
            "Krydder": ["salt", "pepper", "paprika", "karri", "hvitløk"],
        }

        # Categorize shopping list
        shopping_list = {cat: [] for cat in categories}
        shopping_list["Annet"] = []

        for name, items in ingredient_map.items():
            # Determine category
            category = "Annet"
            for cat, keywords in categories.items():
                if any(kw in name for kw in keywords):
                    category = cat
                    break

            # Consolidate quantities (simple sum for now)
            total_amount = sum(
                float(item["amount"]) for item in items if item["amount"].replace(".", "").isdigit()
            )
            unit = items[0]["unit"] if items[0]["unit"] else ""

            shopping_list[category].append(
                {
                    "name": items[0]["name"],
                    "quantity": f"{total_amount} {unit}" if total_amount > 0 else "etter behov",
                    "product_url": items[0].get("product_url"),
                    "count": len(items),  # How many recipes use this
                }
            )

        # Remove empty categories
        shopping_list = {k: v for k, v in shopping_list.items() if v}

        return shopping_list

    def suggest_substitutions(
        self, recipe: Recipe, available_ingredients: list[str]
    ) -> dict[str, list[str]]:
        """Suggest ingredient substitutions based on what's available.

        Args:
            recipe: Recipe to find substitutions for
            available_ingredients: List of ingredients already in plan

        Returns:
            Dictionary mapping recipe ingredients to suggested substitutions
        """
        # Common substitution rules
        substitutions = {
            "brokkoli": ["blomkål", "grønnkål"],
            "gulrot": ["søtpotet", "pastinakk"],
            "paprika": ["tomat", "squash"],
            "kylling": ["kalkun", "svin"],
            "laks": ["torsk", "sei"],
            "pasta": ["ris", "quinoa"],
            "melk": ["havremelk", "fløte"],
        }

        suggestions = {}
        for ingredient in recipe.ingredients:
            ing_name = ingredient.name.lower().strip()

            # Check if any substitution is available
            for original, subs in substitutions.items():
                if original in ing_name:
                    # Filter to only available substitutions
                    available_subs = [
                        s for s in subs if any(s in avail.lower() for avail in available_ingredients)
                    ]
                    if available_subs:
                        suggestions[ingredient.name] = available_subs

        return suggestions
