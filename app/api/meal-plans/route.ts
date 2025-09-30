import { NextResponse } from "next/server"
import type { ApiResponse, MealPlan } from "@/lib/types"
import { store } from "@/lib/store"

export async function GET(): Promise<NextResponse<ApiResponse<MealPlan[]>>> {
  return NextResponse.json({ success: true, data: store.mealPlans })
}

export async function POST(request: Request): Promise<NextResponse<ApiResponse<MealPlan>>> {
  const body = (await request.json().catch(() => null)) as Omit<MealPlan, "id"> | null
  if (!body) return NextResponse.json({ success: false, error: "Invalid body" }, { status: 400 })
  const plan: MealPlan = { id: Date.now().toString(), ...body }
  store.mealPlans.push(plan)
  return NextResponse.json({ success: true, data: plan })
}
