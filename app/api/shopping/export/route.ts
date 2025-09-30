import { NextResponse } from "next/server"
import { store } from "@/lib/store"

export async function GET() {
  const lines = ["Name,Category,Quantity,Unit,Completed,Source"]
  for (const s of store.shopping) {
    lines.push([s.name, s.category, s.quantity, s.unit, s.isCompleted ? "yes" : "no", s.source].join(","))
  }
  const csv = lines.join("\n")
  return NextResponse.json({ success: true, data: csv })
}
