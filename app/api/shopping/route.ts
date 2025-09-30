import { NextResponse } from "next/server"
import type { ApiResponse, ShoppingItem, CreateShoppingItemRequest } from "@/lib/types"
import { store } from "@/lib/store"

export async function GET(): Promise<NextResponse<ApiResponse<ShoppingItem[]>>> {
  return NextResponse.json({ success: true, data: store.shopping })
}

export async function POST(request: Request): Promise<NextResponse<ApiResponse<ShoppingItem>>> {
  const body = (await request.json().catch(() => null)) as CreateShoppingItemRequest | null
  if (!body) return NextResponse.json({ success: false, error: "Invalid body" }, { status: 400 })
  const item: ShoppingItem = {
    id: Date.now().toString(),
    name: body.name,
    category: body.category,
    quantity: body.quantity,
    unit: body.unit,
    isCompleted: false,
    addedDate: new Date().toISOString().split("T")[0],
    source: body.source,
    recipeId: body.recipeId,
    priority: body.priority ?? "medium",
  }
  store.shopping.push(item)
  return NextResponse.json({ success: true, data: item })
}
