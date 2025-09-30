import { NextResponse } from "next/server"
import type { ApiResponse } from "@/lib/types"
import { store } from "@/lib/store"

// Heuristic auto-generation:
// - Replenish items expiring soon (daysLeft <= 2)
// - Ensure ingredients for upcoming meal plans are present; add missing
export async function POST() {
  try {
    const added: Array<{ id: string; name: string; category: string; quantity: string; unit: string; isCompleted: boolean; addedDate: string; source: "manual" | "recipe" | "meal-plan"; recipeId?: string; priority?: "low" | "medium" | "high" }> = []

    const nowDate = new Date().toISOString().split("T")[0]

    // 1) Replenish expiring inventory
    for (const it of store.inventory) {
      if (it.daysLeft <= 2) {
        const exists = store.shopping.find((s) => s.name.toLowerCase() === it.name.toLowerCase() && !s.isCompleted)
        if (!exists) {
          const item = {
            id: Date.now().toString() + Math.random(),
            name: it.name,
            category: it.category || "General",
            quantity: "1",
            unit: it.unit || "unit",
            isCompleted: false,
            addedDate: nowDate,
            source: "meal-plan" as const,
            priority: "high" as const,
          }
          store.shopping.push(item)
          added.push(item)
        }
      }
    }

    // 2) Add missing ingredients for planned recipes
    for (const mp of store.mealPlans) {
      const recipe = store.recipes.find((r) => r.id === mp.recipeId)
      if (!recipe) continue
      for (const ing of recipe.ingredients) {
        const ingName = ing.toLowerCase().split(/,|\d/)[0].trim()
        const inv = store.inventory.find((i) => i.name.toLowerCase().includes(ingName))
        if (!inv) {
          const exists = store.shopping.find((s) => s.name.toLowerCase().includes(ingName) && !s.isCompleted)
          if (!exists) {
            const item = {
              id: Date.now().toString() + Math.random(),
              name: ingName.charAt(0).toUpperCase() + ingName.slice(1),
              category: "General",
              quantity: "1",
              unit: "unit",
              isCompleted: false,
              addedDate: nowDate,
              source: "meal-plan" as const,
              recipeId: recipe.id,
              priority: "medium" as const,
            }
            store.shopping.push(item)
            added.push(item)
          }
        }
      }
    }

    return NextResponse.json({ success: true, data: added } as ApiResponse<any>)
  } catch (e) {
    return NextResponse.json({ success: false, error: "Failed to auto-generate shopping list" } as ApiResponse<any>, { status: 500 })
  }
}
