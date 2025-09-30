import { NextResponse } from "next/server"
import type { ApiResponse } from "@/lib/types"
import { store } from "@/lib/store"

export async function GET() {
  const totalItems = store.inventory.length
  const recipesCooked = store.mealPlans.length
  const wasteReduction = 12 // mock %
  const moneySaved = 34 // mock $
  const favoriteCategories = ["Dairy", "Fruits", "Grains"]
  const monthlyTrends = [
    { month: "Jan", waste: 10, savings: 20 },
    { month: "Feb", waste: 8, savings: 25 },
    { month: "Mar", waste: 7, savings: 30 },
  ]
  return NextResponse.json({ success: true, data: { totalItems, wasteReduction, moneySaved, recipesCooked, favoriteCategories, monthlyTrends } } as ApiResponse<any>)
}
