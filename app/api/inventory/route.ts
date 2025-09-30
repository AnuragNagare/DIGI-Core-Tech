import { type NextRequest, NextResponse } from "next/server"
import type { InventoryItem, CreateInventoryItemRequest, ApiResponse } from "@/lib/types"
import { store } from "@/lib/store"

export async function GET(): Promise<NextResponse<ApiResponse<InventoryItem[]>>> {
  try {
    return NextResponse.json({
      success: true,
      data: store.inventory,
    })
  } catch (error) {
    return NextResponse.json(
      {
        success: false,
        error: "Failed to fetch inventory",
      },
      { status: 500 },
    )
  }
}

export async function POST(request: NextRequest): Promise<NextResponse<ApiResponse<InventoryItem>>> {
  try {
    const body: CreateInventoryItemRequest = await request.json()

    // TODO: Replace with actual database logic
    const newItem: InventoryItem = {
      id: Date.now().toString(),
      ...body,
      addedDate: new Date().toISOString().split("T")[0],
      daysLeft: Math.floor((new Date(body.expiryDate).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24)),
    }

    store.inventory.push(newItem)

    return NextResponse.json({
      success: true,
      data: newItem,
    })
  } catch (error) {
    return NextResponse.json(
      {
        success: false,
        error: "Failed to create inventory item",
      },
      { status: 500 },
    )
  }
}
