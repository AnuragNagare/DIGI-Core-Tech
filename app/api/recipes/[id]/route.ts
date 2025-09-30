import { NextResponse } from "next/server"
import type { ApiResponse, Recipe } from "@/lib/types"
import { store } from "@/lib/store"

export async function GET(_: Request, { params }: { params: { id: string } }): Promise<NextResponse<ApiResponse<Recipe>>> {
  const recipe = store.recipes.find((r) => r.id === params.id)
  if (!recipe) return NextResponse.json({ success: false, error: "Not found" }, { status: 404 })
  return NextResponse.json({ success: true, data: recipe })
}
