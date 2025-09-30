import { NextResponse } from "next/server"
import type { ApiResponse, NotificationSettings } from "@/lib/types"

let settings: NotificationSettings = {
  expiryAlerts: true,
  mealPlanReminders: true,
  shoppingReminders: false,
  wasteReductionTips: true,
  emailNotifications: false,
}

export async function GET() {
  return NextResponse.json({ success: true, data: settings } satisfies ApiResponse<NotificationSettings>)
}

export async function PUT(request: Request) {
  const body = (await request.json().catch(() => ({}))) as Partial<NotificationSettings>
  settings = { ...settings, ...body }
  return NextResponse.json({ success: true, data: settings } satisfies ApiResponse<NotificationSettings>)
}
