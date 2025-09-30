import { NextResponse } from "next/server"
import type { ApiResponse, Recipe } from "@/lib/types"
import { store } from "@/lib/store"

export async function POST(request: Request, { params }: { params: { id: string } }): Promise<NextResponse<ApiResponse<Recipe>>> {
  const { rating } = await request.json().catch(() => ({ rating: undefined }))
  if (typeof rating !== "number") return NextResponse.json({ success: false, error: "Invalid rating" }, { status: 400 })
  const recipe = store.recipes.find((r) => r.id === params.id)
  if (!recipe) return NextResponse.json({ success: false, error: "Not found" }, { status: 404 })
  recipe.rating = rating
  return NextResponse.json({ success: true, data: recipe })
}
