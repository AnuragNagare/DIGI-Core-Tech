import { NextResponse } from "next/server"
import type { ApiResponse } from "@/lib/types"
import { store } from "@/lib/store"

export async function DELETE(_: Request, { params }: { params: { id: string } }): Promise<NextResponse<ApiResponse<void>>> {
  const before = store.mealPlans.length
  store.mealPlans = store.mealPlans.filter((m) => m.id !== params.id)
  if (store.mealPlans.length === before) return NextResponse.json({ success: false, error: "Not found" }, { status: 404 })
  return NextResponse.json({ success: true, data: undefined as any })
}
