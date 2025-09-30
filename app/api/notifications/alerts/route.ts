import { NextResponse } from "next/server"
import type { ApiResponse, InventoryItem } from "@/lib/types"
import { store } from "@/lib/store"

export async function GET() {
  const expiring: InventoryItem[] = store.inventory.filter((i) => i.daysLeft <= 1)
  const reminders: string[] = []
  if (expiring.length > 0) reminders.push(`${expiring.length} item(s) expiring soon`)
  if (store.mealPlans.length > 0) reminders.push("You have meals planned this week")
  return NextResponse.json({ success: true, data: { expiring, reminders } } as ApiResponse<{ expiring: InventoryItem[]; reminders: string[] }>)
}
