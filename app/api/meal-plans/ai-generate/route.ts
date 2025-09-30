import { NextResponse } from "next/server"
import type { ApiResponse, MealPlan } from "@/lib/types"
import { store, suggestAiRecipes } from "@/lib/store"
import { ai } from "@/lib/ai"
import { addDays, format, startOfWeek } from "date-fns"

export async function POST(request: Request): Promise<NextResponse<ApiResponse<Omit<MealPlan, "id">[]>>> {
  try {
    const body = (await request.json().catch(() => ({}))) as {
      startDate?: string
      save?: boolean
      servings?: number
    }
    const start = body.startDate ? new Date(body.startDate) : startOfWeek(new Date())
    const servings = body.servings ?? 2

    let plan: Omit<MealPlan, "id">[] | null = null
    try {
      if (ai.haveAi()) {
        plan = await ai.aiGenerateWeeklyMealPlan(store.recipes, format(start, "yyyy-MM-dd"))
      }
    } catch {
      // ignore AI failure and fallback
    }

    if (!plan) {
      // Fallback: cycle through AI suggestions/heuristic and assign lunch for 7 days
      const suggestions = suggestAiRecipes()
      const picks = suggestions.length > 0 ? suggestions : store.recipes.slice(0, 7)
      plan = Array.from({ length: 7 }).map((_, i) => {
        const date = addDays(start, i)
        const r = picks[i % picks.length]
        return {
          date: format(date, "yyyy-MM-dd"),
          mealType: "dinner",
          recipeId: r.id,
          recipeName: r.name,
          servings,
        }
      })
    }

    if (body.save) {
      for (const p of plan) {
        store.mealPlans.push({ id: Date.now().toString() + Math.random().toString(16).slice(2), ...p })
      }
    }

    return NextResponse.json({ success: true, data: plan })
  } catch (e) {
    return NextResponse.json({ success: false, error: "Failed to generate AI meal plan" }, { status: 500 })
  }
}
