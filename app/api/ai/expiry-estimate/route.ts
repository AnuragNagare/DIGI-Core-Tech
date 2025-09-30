import { NextResponse } from "next/server"
import type { ApiResponse } from "@/lib/types"

// Basic heuristic shelf life (days) as a fallback
const HEURISTIC_SHELF_LIFE: Record<string, number> = {
  banana: 4,
  milk: 5,
  tomato: 5,
  "cherry tomato": 4,
  "roma tomato": 6,
  yogurt: 7,
  chicken: 2,
  beef: 3,
  bread: 4,
  eggs: 21,
  lettuce: 5,
}

export async function POST(request: Request) {
  try {
    const body = (await request.json()) as { imageDataUrl?: string; itemName?: string; condition?: string }

    // If model available, call LLM to estimate shelf life using image and name
    if (process.env.OPENAI_API_KEY && (body.imageDataUrl || body.itemName)) {
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
              { role: "system", content: "Estimate remaining shelf life (days) given a food item and its condition. Return JSON {daysLeft:number, notes:string}." },
              {
                role: "user",
                content: body.imageDataUrl
                  ? [
                      { type: "text", text: `Item: ${body.itemName || "unknown"}. Condition: ${body.condition || "n/a"}.` },
                      { type: "image_url", image_url: { url: body.imageDataUrl } },
                    ]
                  : `Item: ${body.itemName}. Condition: ${body.condition || "n/a"}.` ,
              },
            ],
            temperature: 0.2,
          }),
        })
        if (res.ok) {
          const json = await res.json()
          const text: string = json?.choices?.[0]?.message?.content || "{}"
          let parsed: { daysLeft?: number; notes?: string } = {}
          try { parsed = JSON.parse(text) } catch {}
          if (typeof parsed.daysLeft === "number") {
            return NextResponse.json({ success: true, data: parsed } as ApiResponse<any>)
          }
        }
      } catch {}
    }

    // Heuristic fallback based on itemName
    const name = (body.itemName || "").toLowerCase()
    let baseline = 5
    for (const key of Object.keys(HEURISTIC_SHELF_LIFE)) {
      if (name.includes(key)) { baseline = HEURISTIC_SHELF_LIFE[key]; break }
    }
    return NextResponse.json({ success: true, data: { daysLeft: baseline, notes: "heuristic" } } as ApiResponse<any>)
  } catch (e) {
    return NextResponse.json({ success: false, error: "Expiry estimation failed" } as ApiResponse<any>, { status: 500 })
  }
}
