import type { InventoryItem, MealPlan, Recipe } from "@/lib/types"

const OPENAI_API_KEY = process.env.OPENAI_API_KEY
const OPENAI_BASE_URL = process.env.OPENAI_BASE_URL || "https://api.openai.com/v1"
const OPENAI_MODEL = process.env.OPENAI_MODEL || "gpt-4o-mini"

function haveAi(): boolean {
  return !!OPENAI_API_KEY
}

async function chat(prompt: string): Promise<string> {
  if (!haveAi()) throw new Error("AI not configured")

  const res = await fetch(`${OPENAI_BASE_URL}/chat/completions`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${OPENAI_API_KEY}`,
    },
    body: JSON.stringify({
      model: OPENAI_MODEL,
      messages: [
        { role: "system", content: "You are a helpful meal planning and grocery assistant." },
        { role: "user", content: prompt },
      ],
      temperature: 0.4,
    }),
  })
  if (!res.ok) throw new Error(`AI error: ${res.status}`)
  const json = await res.json()
  const text: string = json?.choices?.[0]?.message?.content || ""
  return text
}

export async function aiSuggestRecipes(recipes: Recipe[], inventory: InventoryItem[], count = 5): Promise<Recipe[]> {
  if (!haveAi()) throw new Error("AI not configured")
  const inv = inventory.map((i) => ({ name: i.name, daysLeft: i.daysLeft, category: i.category })).slice(0, 100)
  const rec = recipes.map((r) => ({ id: r.id, name: r.name, ingredients: r.ingredients, rating: r.rating })).slice(0, 200)

  const prompt = `Given this inventory (with daysLeft) and recipe catalog, return the top ${count} recipe ids best to cook now to reduce waste and maximize rating.
Return a JSON array of recipe ids only.
Inventory: ${JSON.stringify(inv)}
Recipes: ${JSON.stringify(rec)}`

  const raw = await chat(prompt)
  try {
    const ids = JSON.parse(raw.trim()) as string[]
    const picked = ids
      .map((id) => recipes.find((r) => r.id === id))
      .filter((r): r is Recipe => !!r)
    // Ensure unique and limit
    const unique: Recipe[] = []
    for (const r of picked) if (!unique.find((x) => x.id === r.id)) unique.push(r)
    return unique.slice(0, count)
  } catch {
    // If model returned prose, try to extract ids by matching known ids
    const ids = recipes.filter((r) => raw.includes(r.id)).map((r) => r.id)
    const unique: Recipe[] = []
    for (const id of ids) {
      const r = recipes.find((x) => x.id === id)
      if (r && !unique.find((x) => x.id === r.id)) unique.push(r)
    }
    return unique.slice(0, count)
  }
}

export async function aiGenerateWeeklyMealPlan(
  recipes: Recipe[],
  startDateISO: string,
): Promise<Omit<MealPlan, "id">[]> {
  if (!haveAi()) throw new Error("AI not configured")

  const rec = recipes.map((r) => ({ id: r.id, name: r.name, tags: r.tags, cookTime: r.cookTime }))
  const prompt = `Create a 7-day meal plan starting from ${startDateISO}.
Return JSON array of items with fields: date (YYYY-MM-DD), mealType (breakfast|lunch|dinner), recipeId, recipeName, servings (number).
Use provided recipes by id and name.
Recipes: ${JSON.stringify(rec)}`

  const raw = await chat(prompt)
  const parsed = JSON.parse(raw) as Array<{
    date: string
    mealType: "breakfast" | "lunch" | "dinner" | "snack"
    recipeId: string
    recipeName: string
    servings: number
  }>
  return parsed
}

export const ai = { haveAi, aiSuggestRecipes, aiGenerateWeeklyMealPlan }
