import { NextResponse } from "next/server"
import type { ApiResponse, ShoppingItem } from "@/lib/types"
import { store } from "@/lib/store"

const CATEGORY_RULES: Array<{ category: string; keywords: string[] }> = [
  { category: "Vegetables", keywords: ["tomato", "onion", "lettuce", "spinach", "cucumber", "pepper", "broccoli", "carrot", "potato", "basil"] },
  { category: "Fruits", keywords: ["banana", "apple", "orange", "berry", "mango", "grape", "melon", "lemon", "lime"] },
  { category: "Dairy", keywords: ["milk", "yogurt", "cheese", "butter", "cream"] },
  { category: "Meats", keywords: ["chicken", "beef", "pork", "lamb", "fish", "salmon", "tuna"] },
  { category: "Grains", keywords: ["rice", "pasta", "bread", "flour", "oats", "noodle"] },
  { category: "Spices", keywords: ["salt", "pepper", "cumin", "turmeric", "paprika", "chili", "coriander", "garlic"] },
  { category: "Beverages", keywords: ["juice", "soda", "coffee", "tea", "water"] },
  { category: "Frozen", keywords: ["frozen", "ice cream", "peas"] },
  { category: "Bakery", keywords: ["bun", "bagel", "croissant"] },
  { category: "General", keywords: [] },
]

function categorizeName(name: string): string {
  const n = name.toLowerCase()
  for (const rule of CATEGORY_RULES) {
    if (rule.keywords.some((k) => n.includes(k))) return rule.category
  }
  return "General"
}

export async function POST() {
  try {
    // Update categories in-place based on name
    store.shopping.forEach((item) => {
      item.category = categorizeName(item.name)
    })

    // Group by category for response convenience
    const groups: Record<string, ShoppingItem[]> = {}
    for (const item of store.shopping) {
      const key = item.category || "General"
      groups[key] = groups[key] || []
      groups[key].push(item)
    }

    return NextResponse.json({ success: true, data: { groups } } as ApiResponse<any>)
  } catch (e) {
    return NextResponse.json({ success: false, error: "Failed to categorize shopping list" } as ApiResponse<any>, { status: 500 })
  }
}
