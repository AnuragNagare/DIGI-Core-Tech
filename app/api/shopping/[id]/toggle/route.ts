import { NextResponse } from "next/server"
import type { ApiResponse, ShoppingItem } from "@/lib/types"
import { store } from "@/lib/store"

export async function POST(_: Request, { params }: { params: { id: string } }): Promise<NextResponse<ApiResponse<ShoppingItem>>> {
  const item = store.shopping.find((s) => s.id === params.id)
  if (!item) return NextResponse.json({ success: false, error: "Not found" }, { status: 404 })
  item.isCompleted = !item.isCompleted
  return NextResponse.json({ success: true, data: item })
}
