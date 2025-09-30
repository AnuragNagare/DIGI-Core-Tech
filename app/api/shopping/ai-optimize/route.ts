import { NextResponse } from "next/server"
import { ai } from "@/lib/ai"
import { store } from "@/lib/store"
import type { ApiResponse, ShoppingItem } from "@/lib/types"

function heuristicOptimize(items: ShoppingItem[]): ShoppingItem[] {
  const highCats = ["Produce", "Dairy", "Bakery", "Meat", "Seafood"]
  return items.map((it) => ({
    ...it,
    priority: highCats.some((c) => it.category?.toLowerCase().includes(c.toLowerCase())) ? "high" : it.priority || "medium",
  }))
}

export async function POST() {
  try {
    if (store.shopping.length === 0) {
      return NextResponse.json({ success: true, data: [] } as ApiResponse<ShoppingItem[]>)
    }

    // If AI configured, ask it to optimize priorities; fallback to heuristic
    if (ai.haveAi()) {
      try {
        const items = store.shopping.map((i) => ({ id: i.id, name: i.name, category: i.category, priority: i.priority || "medium" }))
        const prompt = `Optimize shopping list priorities (high|medium|low) to minimize waste and shopping time.
Return JSON array of {id, priority}. Items: ${JSON.stringify(items)}`
        // Reuse ai.chat via private function by indirect call: construct a local small wrapper
        const res = await fetch((process.env.OPENAI_BASE_URL || "https://api.openai.com/v1") + "/chat/completions", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${process.env.OPENAI_API_KEY}`,
          },
          body: JSON.stringify({
            model: process.env.OPENAI_MODEL || "gpt-4o-mini",
            messages: [
              { role: "system", content: "You optimize priorities of shopping items for a grocery app." },
              { role: "user", content: prompt },
            ],
            temperature: 0.2,
          }),
        })
        if (res.ok) {
          const json = await res.json()
          const text: string = json?.choices?.[0]?.message?.content || "[]"
          let updates: Array<{ id: string; priority: "high" | "medium" | "low" }> = []
          try {
            updates = JSON.parse(text)
          } catch {
            updates = []
          }
          if (updates.length > 0) {
            const map = new Map(updates.map((u) => [u.id, u.priority]))
            store.shopping = store.shopping.map((it) => ({ ...it, priority: map.get(it.id) || it.priority || "medium" }))
            return NextResponse.json({ success: true, data: store.shopping } as ApiResponse<ShoppingItem[]>)
          }
        }
      } catch {}
    }

    // Heuristic fallback
    store.shopping = heuristicOptimize(store.shopping)
    return NextResponse.json({ success: true, data: store.shopping } as ApiResponse<ShoppingItem[]>)
  } catch (e) {
    return NextResponse.json(
      { success: false, error: "Failed to optimize shopping list" } as ApiResponse<ShoppingItem[]>,
      { status: 500 },
    )
  }
}
