import { NextResponse } from "next/server"
import type { ApiResponse, MealPlan } from "@/lib/types"
import { store } from "@/lib/store"

export async function GET(request: Request): Promise<NextResponse<ApiResponse<MealPlan[]>>> {
  const { searchParams } = new URL(request.url)
  const start = searchParams.get("start")
  if (!start) return NextResponse.json({ success: false, error: "Missing start" }, { status: 400 })
  const startDate = new Date(start)
  const endDate = new Date(startDate)
  endDate.setDate(startDate.getDate() + 6)
  const result = store.mealPlans.filter((p) => {
    const d = new Date(p.date)
    return d >= startDate && d <= endDate
  })
  return NextResponse.json({ success: true, data: result })
}
