import { NextResponse } from "next/server"
import type { ApiResponse } from "@/lib/types"

export async function GET() {
  const totalWaste = 3.2
  const wasteByCategory = [
    { category: "Vegetables", amount: 1.2 },
    { category: "Dairy", amount: 0.9 },
    { category: "Bakery", amount: 1.1 },
  ]
  const suggestions = [
    "Use near-expiry items in soups and stews",
    "Plan meals using perishable ingredients first",
  ]
  return NextResponse.json({ success: true, data: { totalWaste, wasteByCategory, suggestions } } as ApiResponse<any>)
}
