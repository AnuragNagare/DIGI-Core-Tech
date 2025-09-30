import { NextResponse } from "next/server"
import type { ApiResponse } from "@/lib/types"
import { store } from "@/lib/store"

interface ExtractMealRequest {
  imageDataUrl?: string
  notes?: string // optional text description
  deduct?: boolean
  addMissingToShopping?: boolean
}

export async function POST(request: Request) {
  try {
    const body = (await request.json()) as ExtractMealRequest

    // Try AI first if available
    let extracted: Array<{ name: string; quantity: number; unit: string }> = []
    if (process.env.OPENAI_API_KEY && (body.imageDataUrl || body.notes)) {
      try {
        const res = await fetch((process.env.OPENAI_BASE_URL || "https://api.openai.com/v1") + "/chat/completions", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${process.env.OPENAI_API_KEY}`,
          },
          body: JSON.stringify({
            model: process.env.OPENAI_MODEL || "gpt-4o-mini",
            messages: [
              { role: "system", content: "Extract ingredients and quantities from a meal photo or description. Return JSON array of {name, quantity:number, unit}." },
              {
                role: "user",
                content: body.imageDataUrl
                  ? [
                      { type: "text", text: body.notes || "Extract ingredients and amounts." },
                      { type: "image_url", image_url: { url: body.imageDataUrl } },
                    ]
                  : (body.notes || "Extract ingredients and amounts."),
              },
            ],
            temperature: 0.2,
          }),
        })
        if (res.ok) {
          const json = await res.json()
          const text: string = json?.choices?.[0]?.message?.content || "[]"
          try {
            extracted = JSON.parse(text)
          } catch {
            extracted = []
          }
        }
      } catch {}
    }

    // Heuristic fallback
    if (extracted.length === 0 && body.notes) {
      const parts = body.notes.split(/,|\n/).map((p) => p.trim()).filter(Boolean)
      for (const p of parts) {
        const m = p.match(/([A-Za-z][A-Za-z\s\-]+)\s+(\d+(?:\.\d+)?)\s*(kg|g|lb|ml|l|pcs|unit)?/i)
        if (m) extracted.push({ name: m[1].trim(), quantity: parseFloat(m[2]), unit: (m[3] || "unit").toLowerCase() })
      }
    }

    // Optional side-effects: deduct inventory and add missing to shopping
    if (extracted.length > 0 && (body.deduct || body.addMissingToShopping)) {
      for (const ing of extracted) {
        const inv = store.inventory.find((i) => i.name.toLowerCase().includes(ing.name.toLowerCase().split(" ")[0]))
        if (inv) {
          if (body.deduct) {
            const current = Number(inv.quantity) || 0
            const left = Math.max(0, current - ing.quantity)
            inv.quantity = String(left)
          }
        } else if (body.addMissingToShopping) {
          store.shopping.push({
            id: Date.now().toString() + Math.random(),
            name: ing.name,
            category: "General",
            quantity: String(ing.quantity),
            unit: ing.unit || "unit",
            isCompleted: false,
            addedDate: new Date().toISOString().split("T")[0],
            source: "meal-plan",
            priority: "medium",
          })
        }
      }
    }

    return NextResponse.json({ success: true, data: extracted } as ApiResponse<any>)
  } catch (e) {
    return NextResponse.json({ success: false, error: "Meal extraction failed" } as ApiResponse<any>, { status: 500 })
  }
}
