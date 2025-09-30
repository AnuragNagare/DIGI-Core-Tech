import { NextResponse } from "next/server"
import type { ApiResponse, Recipe } from "@/lib/types"
import { suggestAiRecipes, store } from "@/lib/store"
import { ai } from "@/lib/ai"

export async function GET(): Promise<NextResponse<ApiResponse<Recipe[]>>> {
  try {
    let suggestions: Recipe[] | null = null
    try {
      if (ai.haveAi()) {
        suggestions = await ai.aiSuggestRecipes(store.recipes, store.inventory, 5)
      }
    } catch {
      // ignore and fallback
    }
    if (!suggestions || suggestions.length === 0) suggestions = suggestAiRecipes()
    return NextResponse.json({ success: true, data: suggestions })
  } catch (e) {
    return NextResponse.json({ success: false, error: "Failed to get AI suggestions" }, { status: 500 })
  }
}
