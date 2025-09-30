import { NextResponse } from "next/server"
import type { ApiResponse, ShoppingItem } from "@/lib/types"
import { store } from "@/lib/store"

export async function POST(_: Request, { params }: { params: { id: string } }): Promise<NextResponse<ApiResponse<ShoppingItem[]>>> {
  const recipe = store.recipes.find((r) => r.id === params.id)
  if (!recipe) return NextResponse.json({ success: false, error: "Recipe not found" }, { status: 404 })

  const created: ShoppingItem[] = []
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
        source: "recipe",
        recipeId: recipe.id,
        priority: "medium",
      }
      store.shopping.push(item)
      created.push(item)
    }
  }

  return NextResponse.json({ success: true, data: created })
}
