import { type NextRequest, NextResponse } from "next/server"
import type { Recipe, RecipeFilterRequest, ApiResponse } from "@/lib/types"
import { store } from "@/lib/store"

export async function GET(request: NextRequest): Promise<NextResponse<ApiResponse<Recipe[]>>> {
  try {
    const { searchParams } = new URL(request.url)
    const filters: RecipeFilterRequest = {
      cuisine: searchParams.get("cuisine") || undefined,
      difficulty: searchParams.get("difficulty") || undefined,
      cookTime: searchParams.get("cookTime") || undefined,
      dietary: searchParams.get("dietary") || undefined,
      search: searchParams.get("search") || undefined,
      canMakeWithInventory: searchParams.get("canMakeWithInventory") === "true",
    }

    let filteredRecipes = store.recipes

    // Apply filters
    if (filters.search) {
      filteredRecipes = filteredRecipes.filter(
        (recipe) =>
          recipe.name.toLowerCase().includes(filters.search!.toLowerCase()) ||
          recipe.description.toLowerCase().includes(filters.search!.toLowerCase()),
      )
    }

    if (filters.cuisine && filters.cuisine !== "all") {
      filteredRecipes = filteredRecipes.filter((recipe) => recipe.cuisine === filters.cuisine)
    }

    if (filters.difficulty && filters.difficulty !== "all") {
      filteredRecipes = filteredRecipes.filter((recipe) => recipe.difficulty === filters.difficulty)
    }

    if (filters.canMakeWithInventory) {
      filteredRecipes = filteredRecipes.filter((recipe) => recipe.canMakeWithInventory)
    }

    return NextResponse.json({
      success: true,
      data: filteredRecipes,
    })
  } catch (error) {
    return NextResponse.json(
      {
        success: false,
        error: "Failed to fetch recipes",
      },
      { status: 500 },
    )
  }
}
