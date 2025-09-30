import { NextResponse } from "next/server"
import type { ApiResponse, ShoppingItem } from "@/lib/types"
import { store } from "@/lib/store"

export async function POST(): Promise<NextResponse<ApiResponse<ShoppingItem[]>>> {
  const created: ShoppingItem[] = []
  const weekStart = new Date()
  weekStart.setHours(0, 0, 0, 0)
  const weekEnd = new Date(weekStart)
  weekEnd.setDate(weekStart.getDate() + 6)

  const weekPlans = store.mealPlans.filter((p) => {
    const d = new Date(p.date)
    return d >= weekStart && d <= weekEnd
  })

  for (const plan of weekPlans) {
    const recipe = store.recipes.find((r) => r.id === plan.recipeId)
    if (recipe) {
      for (const ing of recipe.missingIngredients) {
        const exists = store.shopping.find((s) => s.name.toLowerCase() === ing.toLowerCase())
        if (!exists) {
          const item: ShoppingItem = {
            id: Date.now().toString() + Math.random().toString(16).slice(2),
            name: ing,
            category: "Other",
            quantity: "1",
            unit: "item",
            isCompleted: false,
            addedDate: new Date().toISOString().split("T")[0],
            source: "meal-plan",
            recipeId: recipe.id,
            priority: "medium",
          }
          store.shopping.push(item)
          created.push(item)
        }
      }
    }
  }

  return NextResponse.json({ success: true, data: created })
}
