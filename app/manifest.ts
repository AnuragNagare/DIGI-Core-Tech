import type { MetadataRoute } from "next"

export const dynamic = 'force-static'

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "Smart Grocery App",
    short_name: "Groceries",
    description: "AI-powered recipes, meal plans, and shopping list management",
    start_url: "/",
    scope: "/",
    display: "standalone",
    theme_color: "#0ea5e9",
    background_color: "#ffffff",
    lang: "en",
    orientation: "portrait-primary",
    categories: ["food", "utilities", "productivity"],
  }
}