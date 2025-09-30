import type { InventoryItem, Recipe, ShoppingItem, MealPlan, PurchasedItem } from "@/lib/types"

// In-memory store for demo purposes. Replace with a real DB later.
export const store = {
  inventory: [] as InventoryItem[],
  purchases: [] as PurchasedItem[],
  recipes: [
    {
      id: "1",
      name: "Banana Bread",
      description: "Moist and delicious banana bread perfect for breakfast or snack time",
      cookTime: "60",
      prepTime: "15",
      servings: 8,
      difficulty: "Easy",
      cuisine: "American",
      ingredients: [
        "3 ripe bananas",
        "1/3 cup melted butter",
        "3/4 cup sugar",
        "1 egg",
        "1 tsp vanilla",
        "1 tsp baking soda",
        "Pinch of salt",
        "1 1/2 cups flour",
      ],
      instructions: [
        "Preheat oven to 350°F (175°C)",
        "Mash bananas in a large bowl until smooth",
        "Mix in melted butter until well combined",
        "Add sugar, egg, and vanilla extract, mix well",
        "Sprinkle baking soda and salt over mixture and stir",
        "Add flour and mix until just combined (don't overmix)",
        "Pour batter into greased 9x5 inch loaf pan",
        "Bake for 60 minutes or until golden brown and toothpick comes out clean",
        "Cool in pan for 10 minutes, then turn out onto wire rack",
      ],
      tags: ["breakfast", "sweet", "easy", "baking"],
      rating: 4.5,
      isFavorite: true,
      canMakeWithInventory: true,
      missingIngredients: ["flour", "sugar"],
      calories: 280,
      protein: "4g",
      carbs: "58g",
      fat: "6g",
      dietaryLabels: ["Vegetarian"],
      nutritionScore: 7,
    },
  ] as Recipe[],
  shopping: [] as ShoppingItem[],
  mealPlans: [] as MealPlan[],
}

export function suggestAiRecipes(): Recipe[] {
  // Simple heuristic: prioritize recipes that use items expiring soon
  const useSoon = store.inventory.filter((i) => i.daysLeft <= 3)
  const prioritized = store.recipes
    .map((r) => {
      const score = r.ingredients.reduce((sum, ing) => {
        const match = useSoon.find((it) => it.name.toLowerCase().includes(ing.toLowerCase().split(" ")[0]))
        return sum + (match ? 1 : 0)
      }, 0)
      return { r, score }
    })
    .filter((x) => x.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, 5)
    .map((x) => x.r)

  // Fallback: top rated
  if (prioritized.length === 0) {
    return [...store.recipes].sort((a, b) => (b.rating || 0) - (a.rating || 0)).slice(0, 5)
  }
  return prioritized
}
