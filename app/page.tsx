"use client"
import { useState, useEffect } from "react"
import type React from "react"



import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Checkbox } from "@/components/ui/checkbox"
import { Textarea } from "@/components/ui/textarea"
import { Switch } from "@/components/ui/switch"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  Home,
  ChefHat,
  ShoppingCart,
  Bell,
  Plus,
  Search,
  Calendar,
  Clock,
  Users,
  AlertTriangle,
  CheckCircle,
  Heart,
  Download,
  Settings,
  Scan,
  ReceiptText,
  Package,
  Brain,
  Utensils,
  Edit,
  Trash2,
  Filter,
  Star,
  Play,
  BarChart3,
  Target,
  TrendingUp,
  ShoppingBag,
  Zap,
  BookOpen,
  Timer,
  Leaf,
  Award,
  Eye,
  Share2,
  ListChecks,
  Sparkles,
  X,
  Camera,
  UploadCloud,
} from "lucide-react"
import { format, differenceInDays, parseISO, addDays, startOfWeek } from "date-fns"
import { cn } from "@/lib/utils"
import { recipeApi, shoppingApi, mealPlanApi, aiApi, ocrApi } from "@/lib/api"
import { useToast } from "@/hooks/use-toast"
import { useApi } from "@/lib/hooks/useApi"
import FoodClassifier from "@/components/FoodClassifier"
import AIMealGenerator from "@/components/AIMealGenerator"
import FamilyDashboard from "@/components/family/FamilyDashboard"
import TrackingPage from "@/components/tracking/TrackingPage"

// Helpers: map unit/category and compute expiry
const normalizeUnit = (u?: string) => {
  const s = (u || "").toLowerCase()
  if (["g", "gram", "grams"].includes(s)) return "g"
  if (["kg", "kilogram", "kilograms"].includes(s)) return "kg"
  if (["ml", "milliliter", "milliliters"].includes(s)) return "ml"
  if (["l", "liter", "liters"].includes(s)) return "liter"
  if (["pc", "pcs", "piece", "pieces", "ct", "count"].includes(s)) return "pieces"
  return s || "pieces"
}

const guessCategory = (name: string): string => {
  const n = name.toLowerCase()
  if (/(banana|apple|orange|fruit|berry|grape)/.test(n)) return "Fruits"
  if (/(milk|yogurt|cheese|butter|cream)/.test(n)) return "Dairy"
  if (/(chicken|beef|pork|meat|lamb|turkey)/.test(n)) return "Meat"
  if (/(lettuce|tomato|onion|carrot|broccoli|spinach|vegetable)/.test(n)) return "Vegetables"
  if (/(bread|flour|rice|pasta|grain|cereal)/.test(n)) return "Grains"
  if (/(water|juice|soda|drink|beverage)/.test(n)) return "Beverages"
  if (/(salt|sugar|spice|oil|sauce)/.test(n)) return "Pantry"
  return "Other"
}

const categoryShelfLifeDays = (category: string): number => {
  switch (category) {
    case "Fruits":
    case "Vegetables":
      return 5
    case "Meat":
      return 3
    case "Dairy":
      return 7
    case "Beverages":
      return 30
    case "Grains":
    case "Pantry":
      return 120
    default:
      return 14
  }
}

const parseQuantityUnit = (q?: string): { qty: string; unit: string } => {
  if (!q) return { qty: "1", unit: "pieces" }
  const trimmed = q.toString().trim()
  // Try patterns like "500 g", "1 kg", "2x", "2 pcs"
  const m = trimmed.match(/^(\d+(?:[\.,]\d+)?)\s*([a-zA-Z]+)?/)
  if (m) {
    const qtyNum = m[1].replace(",", ".")
    const unitRaw = normalizeUnit(m[2])
    return { qty: qtyNum, unit: unitRaw || "pieces" }
  }
  return { qty: "1", unit: "pieces" }
}

type Page = "dashboard" | "recipes" | "shopping" | "alerts" | "family" | "tracking"
type RecipeView = "ai" | "all" | "favorites" | "meal-plan"
type ShoppingView = "list" | "categories" | "meal-plan" | "ai"

interface FamilyMember {
  id: string
  name: string
  avatar: string
  dietaryRestrictions: string[]
  favoriteIngredients: string[]
  consumptionData: {
    totalItems: number
    personalMeals: number
    groupMeals: number
    topIngredients: { name: string; quantity: number }[]
  }
}

interface ConsumptionEntry {
  id: string
  memberId: string
  memberName: string
  itemName: string
  quantity: number
  date: string
  mealType: "personal" | "group"
  category: string
}

interface InventoryItem {
  id: string
  name: string
  quantity: string
  unit: string
  category: string
  expiryDate: string
  addedDate: string
  daysLeft: number
  usedQuantity?: string
  notes?: string
}

interface Recipe {
  id: string
  name: string
  description: string
  cookTime: string
  prepTime: string
  servings: number
  difficulty: "Easy" | "Medium" | "Hard"
  cuisine: string
  ingredients: string[]
  instructions: string[]
  tags: string[]
  rating: number
  isFavorite: boolean
  canMakeWithInventory: boolean
  missingIngredients: string[]
  image?: string
  calories?: number
  protein?: string
  carbs?: string
  fat?: string
  dietaryLabels?: string[]
  nutritionScore?: number
}

interface ShoppingItem {
  id: string
  name: string
  category: string
  quantity: string
  unit: string
  isCompleted: boolean
  addedDate: string
  source: "manual" | "recipe" | "meal-plan"
  recipeId?: string
  priority?: "low" | "medium" | "high"
}

interface MealPlan {
  id: string
  date: string
  mealType: "breakfast" | "lunch" | "dinner" | "snack"
  recipeId: string
  recipeName: string
  servings: number
}

interface NotificationSettings {
  expiryAlerts: boolean
  mealPlanReminders: boolean
  shoppingReminders: boolean
  wasteReductionTips: boolean
  emailNotifications: boolean
}

interface MealRecord {
  id: string
  memberId: string
  memberName: string
  mealName: string
  photo?: string
  ingredients: Array<{
    itemId: string
    itemName: string
    quantity: number
    unit: string
  }>
  extraIngredients: Array<{
    name: string
    quantity: string
    unit: string
  }>
  mealType: "personal" | "group"
  date: string
  time: string
}

interface IngredientSelection {
  itemId: string
  itemName: string
  availableQuantity: number
  selectedQuantity: number
  unit: string
}

const recipeDatabase: Recipe[] = [
  {
    id: "1",
    name: "Banana Bread",
    description: "Moist and delicious banana bread perfect for breakfast or snack time",
    cookTime: "60",
    prepTime: "15",
    servings: 8,
    difficulty: "Easy",
    cuisine: "American",
    ingredients: [
      "3 ripe bananas",
      "1/3 cup melted butter",
      "3/4 cup sugar",
      "1 egg",
      "1 tsp vanilla",
      "1 tsp baking soda",
      "Pinch of salt",
      "1 1/2 cups flour",
    ],
    instructions: [
      "Preheat oven to 350°F (175°C)",
      "Mash bananas in a large bowl until smooth",
      "Mix in melted butter until well combined",
      "Add sugar, egg, and vanilla extract, mix well",
      "Sprinkle baking soda and salt over mixture and stir",
      "Add flour and mix until just combined (don't overmix)",
      "Pour batter into greased 9x5 inch loaf pan",
      "Bake for 60 minutes or until golden brown and toothpick comes out clean",
      "Cool in pan for 10 minutes, then turn out onto wire rack",
    ],
    tags: ["breakfast", "sweet", "easy", "baking"],
    rating: 4.5,
    isFavorite: true,
    canMakeWithInventory: true,
    missingIngredients: ["flour", "sugar"],
    calories: 280,
    protein: "4g",
    carbs: "58g",
    fat: "6g",
    dietaryLabels: ["Vegetarian"],
    nutritionScore: 7,
  },
  {
    id: "2",
    name: "Greek Yogurt Parfait",
    description: "Healthy and refreshing parfait with yogurt, fruits, and granola",
    cookTime: "0",
    prepTime: "5",
    servings: 1,
    difficulty: "Easy",
    cuisine: "Mediterranean",
    ingredients: ["1 cup Greek yogurt", "1/4 cup granola", "1/2 cup mixed berries", "1 tbsp honey", "1 tsp chia seeds"],
    instructions: [
      "Add half the yogurt to a glass or bowl",
      "Layer with half the berries and granola",
      "Add remaining yogurt",
      "Top with remaining berries, granola, and chia seeds",
      "Drizzle with honey",
      "Serve immediately for best texture",
    ],
    tags: ["healthy", "breakfast", "quick", "no-cook"],
    rating: 4.2,
    isFavorite: false,
    canMakeWithInventory: true,
    missingIngredients: [],
    calories: 320,
    protein: "20g",
    carbs: "35g",
    fat: "12g",
    dietaryLabels: ["Vegetarian", "Gluten-Free"],
    nutritionScore: 9,
  },
  {
    id: "3",
    name: "Chicken Stir Fry",
    description: "Quick and healthy chicken stir fry with fresh vegetables",
    cookTime: "15",
    prepTime: "10",
    servings: 4,
    difficulty: "Medium",
    cuisine: "Asian",
    ingredients: [
      "1 lb chicken breast, sliced",
      "2 cups mixed vegetables",
      "2 tbsp soy sauce",
      "1 tbsp sesame oil",
      "2 cloves garlic",
      "1 tsp ginger",
      "2 tbsp vegetable oil",
      "1 tbsp cornstarch",
    ],
    instructions: [
      "Slice chicken breast into thin strips",
      "Marinate chicken with soy sauce and cornstarch for 10 minutes",
      "Heat vegetable oil in a large wok or skillet over high heat",
      "Add chicken and cook until golden brown, about 5-6 minutes",
      "Add garlic and ginger, stir for 30 seconds",
      "Add mixed vegetables and stir fry for 3-4 minutes",
      "Add sesame oil and remaining soy sauce",
      "Serve immediately over rice",
    ],
    tags: ["dinner", "healthy", "quick", "protein"],
    rating: 4.7,
    isFavorite: true,
    canMakeWithInventory: false,
    missingIngredients: ["chicken breast", "soy sauce", "sesame oil"],
    calories: 285,
    protein: "28g",
    carbs: "12g",
    fat: "14g",
    dietaryLabels: ["High Protein", "Dairy-Free"],
    nutritionScore: 8,
  },
]

export default function SmartGroceryApp() {
  const { toast } = useToast()
  const [currentPage, setCurrentPage] = useState<Page>("dashboard")
  const [recipeView, setRecipeView] = useState<RecipeView>("ai")
  const [shoppingView, setShoppingView] = useState<ShoppingView>("list")

  const [selectedRecipe, setSelectedRecipe] = useState<Recipe | null>(null)
  const [selectedInventoryItem, setSelectedInventoryItem] = useState<InventoryItem | null>(null)
  const [showInventoryTable, setShowInventoryTable] = useState(false)
  const [showMealPlanner, setShowMealPlanner] = useState(false)
  const [showAnalytics, setShowAnalytics] = useState(false)
  const [showFoodClassifier, setShowFoodClassifier] = useState(false)
  const [showAIMealGenerator, setShowAIMealGenerator] = useState(false)
  const [inventorySearchTerm, setInventorySearchTerm] = useState("")
  const [inventoryFilter, setInventoryFilter] = useState("all")
  const [recipeFilter, setRecipeFilter] = useState({
    cuisine: "all",
    difficulty: "all",
    cookTime: "all",
    dietary: "all",
  })

  const [inventory, setInventory] = useState<InventoryItem[]>([
    {
      id: "1",
      name: "Bananas",
      quantity: "6",
      unit: "pieces",
      category: "Fruits",
      expiryDate: "2024-01-15",
      addedDate: "2024-01-10",
      daysLeft: 3,
      usedQuantity: "2",
      notes: "Perfect for banana bread",
    },
    {
      id: "2",
      name: "Milk",
      quantity: "1",
      unit: "liter",
      category: "Dairy",
      expiryDate: "2024-01-18",
      addedDate: "2024-01-08",
      daysLeft: 6,
      usedQuantity: "0.5",
    },
    {
      id: "3",
      name: "Greek Yogurt",
      quantity: "500",
      unit: "g",
      category: "Dairy",
      expiryDate: "2024-01-14",
      addedDate: "2024-01-09",
      daysLeft: 2,
      usedQuantity: "100",
    },
    {
      id: "4",
      name: "Eggs",
      quantity: "12",
      unit: "pieces",
      category: "Proteins",
      expiryDate: "2024-01-20",
      addedDate: "2024-01-10",
      daysLeft: 8,
      usedQuantity: "0",
    },
    {
      id: "5",
      name: "Chicken Breast",
      quantity: "500",
      unit: "g",
      category: "Proteins",
      expiryDate: "2024-01-16",
      addedDate: "2024-01-11",
      daysLeft: 4,
      usedQuantity: "0",
    },
    {
      id: "6",
      name: "Tomatoes",
      quantity: "4",
      unit: "pieces",
      category: "Vegetables",
      expiryDate: "2024-01-17",
      addedDate: "2024-01-12",
      daysLeft: 5,
      usedQuantity: "1",
    },
    {
      id: "7",
      name: "Onions",
      quantity: "3",
      unit: "pieces",
      category: "Vegetables",
      expiryDate: "2024-01-25",
      addedDate: "2024-01-10",
      daysLeft: 13,
      usedQuantity: "1",
    },
    {
      id: "8",
      name: "Rice",
      quantity: "2",
      unit: "cups",
      category: "Grains",
      expiryDate: "2025-01-01",
      addedDate: "2024-01-08",
      daysLeft: 365,
      usedQuantity: "0.5",
    },
    {
      id: "9",
      name: "Pasta",
      quantity: "500",
      unit: "g",
      category: "Grains",
      expiryDate: "2024-12-15",
      addedDate: "2024-01-07",
      daysLeft: 350,
      usedQuantity: "0",
    },
    {
      id: "10",
      name: "Bell Peppers",
      quantity: "2",
      unit: "pieces",
      category: "Vegetables",
      expiryDate: "2024-01-19",
      addedDate: "2024-01-12",
      daysLeft: 7,
      usedQuantity: "0",
    },
  ])

  const [shoppingList, setShoppingList] = useState<ShoppingItem[]>([
    {
      id: "1",
      name: "Flour",
      category: "Baking",
      quantity: "2",
      unit: "kg",
      isCompleted: false,
      addedDate: "2024-01-12",
      source: "recipe",
      recipeId: "1",
      priority: "high",
    },
    {
      id: "2",
      name: "Eggs",
      category: "Dairy",
      quantity: "12",
      unit: "pieces",
      isCompleted: true,
      addedDate: "2024-01-11",
      source: "manual",
      priority: "medium",
    },
  ])

  const [recipes, setRecipes] = useState<Recipe[]>(recipeDatabase)
  const [searchTerm, setSearchTerm] = useState("")

  const [mealPlans, setMealPlans] = useState<MealPlan[]>([])
  const [notificationSettings, setNotificationSettings] = useState<NotificationSettings>({
    expiryAlerts: true,
    mealPlanReminders: true,
    shoppingReminders: false,
    wasteReductionTips: true,
    emailNotifications: false,
  })

  const [familyMembers, setFamilyMembers] = useState<FamilyMember[]>([
    {
      id: "1",
      name: "Mom",
      avatar: "👩‍🍳",
      dietaryRestrictions: ["Gluten-Free"],
      favoriteIngredients: ["Chicken", "Broccoli", "Rice"],
      consumptionData: {
        totalItems: 45,
        personalMeals: 12,
        groupMeals: 8,
        topIngredients: [
          { name: "Chicken", quantity: 2.5 },
          { name: "Broccoli", quantity: 1.8 },
          { name: "Rice", quantity: 3.2 },
        ],
      },
    },
    {
      id: "2",
      name: "Dad",
      avatar: "👨‍🍳",
      dietaryRestrictions: ["Low-Sodium"],
      favoriteIngredients: ["Beef", "Potatoes", "Carrots"],
      consumptionData: {
        totalItems: 38,
        personalMeals: 15,
        groupMeals: 8,
        topIngredients: [
          { name: "Beef", quantity: 3.1 },
          { name: "Potatoes", quantity: 2.4 },
          { name: "Carrots", quantity: 1.6 },
        ],
      },
    },
    {
      id: "3",
      name: "Alex",
      avatar: "🧑‍🎓",
      dietaryRestrictions: ["Vegetarian"],
      favoriteIngredients: ["Pasta", "Cheese", "Tomatoes"],
      consumptionData: {
        totalItems: 28,
        personalMeals: 20,
        groupMeals: 5,
        topIngredients: [
          { name: "Pasta", quantity: 2.8 },
          { name: "Cheese", quantity: 1.9 },
          { name: "Tomatoes", quantity: 2.1 },
        ],
      },
    },
  ])

  const [consumptionHistory, setConsumptionHistory] = useState<ConsumptionEntry[]>([
    {
      id: "1",
      memberId: "1",
      memberName: "Mom",
      itemName: "Chicken Breast",
      quantity: 0.5,
      date: "2024-01-15",
      mealType: "group",
      category: "Protein",
    },
    {
      id: "2",
      memberId: "2",
      memberName: "Dad",
      itemName: "Ground Beef",
      quantity: 0.3,
      date: "2024-01-15",
      mealType: "personal",
      category: "Protein",
    },
    {
      id: "3",
      memberId: "3",
      memberName: "Alex",
      itemName: "Pasta",
      quantity: 0.2,
      date: "2024-01-14",
      mealType: "personal",
      category: "Grains",
    },
    {
      id: "4",
      memberId: "1",
      memberName: "Mom",
      itemName: "Broccoli",
      quantity: 0.4,
      date: "2024-01-14",
      mealType: "group",
      category: "Vegetables",
    },
    {
      id: "5",
      memberId: "2",
      memberName: "Dad",
      itemName: "Potatoes",
      quantity: 0.6,
      date: "2024-01-13",
      mealType: "group",
      category: "Vegetables",
    },
  ])

  const [selectedMember, setSelectedMember] = useState<FamilyMember | null>(null)
  const [showMealRecorder, setShowMealRecorder] = useState(false)
  const [selectedRecorderMember, setSelectedRecorderMember] = useState<string>("")
  const [mealPhoto, setMealPhoto] = useState<string>("")
  const [mealName, setMealName] = useState("")
  const [mealType, setMealType] = useState<"personal" | "group">("personal")
  const [ingredientSelections, setIngredientSelections] = useState<IngredientSelection[]>([])
  const [extraIngredients, setExtraIngredients] = useState<{ name: string; quantity: string; unit: string }[]>([])
  const [mealRecords, setMealRecords] = useState<MealRecord[]>([])

  // Receipt OCR state
  const [showReceiptDialog, setShowReceiptDialog] = useState(false)
  const [receiptImage, setReceiptImage] = useState<string>("")
  const [receiptFileName, setReceiptFileName] = useState<string>("")
  const [receiptFileType, setReceiptFileType] = useState<string>("")
  const [receiptResult, setReceiptResult] = useState<
    | {
        items: Array<{ name: string; quantity: string; unit: string; price?: number; date?: string }>
        purchaseDate?: string
        rawText?: string
      }
    | null
  >(null)

  const [isUploading, setIsUploading] = useState(false)

  const handleReceiptUpload = async (file: File) => {
    if (!file) {
      console.error("No file provided")
      toast({ title: "Error", description: "No file was selected." })
      return
    }

    setIsUploading(true)
    
    try {
      // Create a preview of the file
      let imageUrl = '';
      if (file.type === 'application/pdf') {
        // For PDF, we'll use a placeholder icon since we can't preview PDF directly
        imageUrl = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjQiIGhlaWdodD0iNjQiIHZpZXdCb3g9IjAgMCA2NCA2NCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTQwIDhIMTJDMTAuOSA4IDEwIDguOSAxMCAxMFY1NEMxMCA1NS4xIDEwLjkgNTYgMTIgNTZINTJDNTMuMSA1NiA1NCA1NS4xIDU0IDU0VjI0TDQwIDhaIiBzdHJva2U9IiM2YjcyODAiIHN0cm9rZS13aWR0aD0iMiIvPgo8cGF0aCBkPSJNNDAgOFYyNEg1NCIgc3Ryb2tlPSIjNmI3MjgwIiBzdHJva2Utd2lkdGg9IjIiLz4KPHN2ZyB4PSIxOCIgeT0iMTYiIHdpZHRoPSIyOCIgaGVpZ2h0PSIyOCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPgo8cGF0aCBkPSJNMTQgMkgyQzAuOSAyIDAgMi45IDAgNFYxOEMwIDE5LjEgMC45IDIwIDIgMjBIMTJDMTMuMSAyMCAxNCAxOS4xIDE0IDE4VjRIMTRaIiBmaWxsPSIjNmI3MjgwIi8+CjxwYXRoIGQ9Ik0xNCAyVjhIMjAiIGZpbGw9IiM2YjcyODAiLz4KPC9zdmc+Cjwvc3ZnPgo=';
      } else {
        imageUrl = URL.createObjectURL(file);
      }
      setReceiptImage(imageUrl)
      setReceiptFileType(file.type || "Unknown type")
      
      // Read the file as base64 for the API
      const base64Image = await new Promise<string>((resolve, reject) => {
        const reader = new FileReader()
        reader.onload = () => {
          const result = reader.result as string;
          resolve(result);
        }
        reader.onerror = (error) => {
          console.error("FileReader error:", error)
          reject(new Error("Could not read the receipt file."))
        }
        reader.readAsDataURL(file)
      })

      console.log("Calling OCR API...")
      const res = await ocrApi.receipt(base64Image).catch(error => {
        console.error("OCR API call failed:", error)
        throw new Error("Failed to connect to the receipt processing service.")
      })
      
      console.log("OCR API response:", res)

      if (!res) {
        throw new Error("No response from receipt processing service")
      }

      // Handle case where the API returns an error
      if (!res.success) {
        throw new Error(res.error || "Failed to process receipt")
      }

      // If we have data, process it
      if (res.data) {
        const data = res.data
        console.log("Parsed receipt data:", data)
        
        // Check if we have items to process
        if (!data.items || !Array.isArray(data.items) || data.items.length === 0) {
          console.warn("No items found in receipt, attempting fallback processing...")
          // Instead of throwing error, provide helpful feedback
          toast({
            title: "Receipt Processing",
            description: "Could not automatically identify items. Please review the extracted text and add items manually.",
            variant: "default",
            duration: 5000,
          })
          
          // Still set the receipt result so user can see what was extracted
          setReceiptResult({
            items: [],
            purchaseDate: new Date().toISOString().split('T')[0],
            rawText: (data as any).rawText || "No text extracted"
          })
          
          // Allow manual processing
          setIsUploading(false)
          return
        }
        
        setReceiptResult(data)
        
        // Process items after a short delay to show the parsed results first
        setTimeout(() => {
          try {
            const items = data.items || []
            let added = 0
            
            items.forEach((it: any) => {
              if (!it?.name) return
              
              const { qty, unit } = parseQuantityUnit(it.quantity || "")
              const normalizedUnit = normalizeUnit(it.unit || unit)
              const category = guessCategory(it.name)
              const baseDateStr = it.date || data.purchaseDate
              const baseDate = baseDateStr ? (isNaN(Date.parse(baseDateStr)) ? new Date() : new Date(baseDateStr)) : new Date()
              const expiryDays = categoryShelfLifeDays(category)
              const expiryDate = format(addDays(baseDate, expiryDays), "yyyy-MM-dd")
              
              const newItem = {
                name: it.name.trim(),
                quantity: qty || "1",
                unit: normalizedUnit || "unit",
                category,
                expiryDate,
                notes: "Added from receipt OCR",
              }
              
              console.log("Adding item to inventory:", newItem)
              addInventoryItem(newItem)
              added += 1
            })
            
            if (added > 0) {
              toast({
                title: "Items Added",
                description: `Successfully added ${added} items from receipt.`,
                variant: "default",
              })
            } else {
              throw new Error("No valid items found in the receipt")
            }
          } catch (processError) {
            console.error("Error processing receipt items:", processError)
            toast({
              title: "Processing Error",
              description: "Could not process all items from the receipt.",
              variant: "destructive",
            })
          }
        }, 1000)
      } else {
        throw new Error("No data received from receipt processing")
      }
    } catch (error) {
      console.error("Error in handleReceiptUpload:", error)
      setReceiptImage("")
      setReceiptResult(null)
      
      const errorMessage = error instanceof Error ? error.message : "An unexpected error occurred"
      toast({
        title: "Receipt Processing Failed",
        description: errorMessage,
        variant: "destructive",
      })
    } finally {
      setIsUploading(false)
    }
  }

  // Calculate status counts
  const freshItems = inventory.filter((item) => item.daysLeft > 3)
  const useSoonItems = inventory.filter((item) => item.daysLeft <= 3 && item.daysLeft > 0)
  const expiringItems = inventory.filter((item) => item.daysLeft <= 0)

  // AI suggestions from backend (auto-updates when inventory/mealPlans change)
  const {
    data: aiData,
    loading: _aiLoading,
    error: _aiError,
  } = useApi(() => recipeApi.getAiSuggestions(), [inventory, mealPlans])
  const aiSuggestions = (aiData && aiData.length > 0
    ? aiData
    : recipes
        .filter(
          (recipe) =>
            recipe.canMakeWithInventory &&
            recipe.ingredients.some((ingredient) =>
              useSoonItems.some((item) => item.name.toLowerCase().includes(ingredient.toLowerCase().split(" ")[0])),
            ),
        )
        .slice(0, 3)) as Recipe[]

  const addInventoryItem = (item: Omit<InventoryItem, "id" | "daysLeft" | "addedDate">) => {
    const newItem: InventoryItem = {
      ...item,
      id: Date.now().toString(),
      addedDate: format(new Date(), "yyyy-MM-dd"),
      daysLeft: differenceInDays(parseISO(item.expiryDate), new Date()),
    }
    setInventory((prev) => [newItem, ...prev])
  }

  const updateInventoryItem = (id: string, updates: Partial<InventoryItem>) => {
    setInventory((prev) =>
      prev.map((item) =>
        item.id === id
          ? {
              ...item,
              ...updates,
              daysLeft: updates.expiryDate ? differenceInDays(parseISO(updates.expiryDate), new Date()) : item.daysLeft,
            }
          : item,
      ),
    )
  }

  const deleteInventoryItem = (id: string) => {
    setInventory((prev) => prev.filter((item) => item.id !== id))
  }

  const addShoppingItem = (item: Omit<ShoppingItem, "id" | "addedDate">) => {
    const newItem: ShoppingItem = {
      ...item,
      id: Date.now().toString(),
      addedDate: format(new Date(), "yyyy-MM-dd"),
    }
    setShoppingList((prev) => [...prev, newItem])
  }

  const generateShoppingListFromRecipe = async (recipe: Recipe) => {
    await shoppingApi.generateFromRecipe(recipe.id)
    const res = await shoppingApi.getAll()
    if (res.success && res.data) setShoppingList(res.data)
  }

  // Generate smart waste-reduction recipe suggestions
  const generateWasteReductionSuggestions = () => {
    const expiringItems = inventory.filter(item => (item.daysLeft || 999) <= 3)
    const highQuantityItems = inventory.filter(item => parseFloat(item.quantity) >= 5)
    const suggestions = []

    // Priority 1: Items expiring soon (≤3 days)
    if (expiringItems.length > 0) {
      suggestions.push({
        id: 'waste-1',
        title: '🚨 Use Before Spoiling',
        items: expiringItems.slice(0, 3),
        reason: `${expiringItems.length} items expiring in ≤3 days`,
        priority: 'urgent',
        recipes: [
          `Quick ${expiringItems[0]?.name} Recipe`,
          `Rescue ${expiringItems.slice(0,2).map(i => i.name).join(' & ')} Bowl`
        ]
      })
    }

    // Priority 2: High quantity items (≥5 units) 
    if (highQuantityItems.length > 0) {
      suggestions.push({
        id: 'waste-2', 
        title: '📦 Bulk Usage',
        items: highQuantityItems.slice(0, 2),
        reason: `Use up large quantities efficiently`,
        priority: 'high',
        recipes: [
          `${highQuantityItems[0]?.name} Meal Prep`,
          `Batch ${highQuantityItems[0]?.name} Recipe`
        ]
      })
    }

    // Priority 3: Items expiring in 4-7 days
    const soonExpiringItems = inventory.filter(item => {
      const days = item.daysLeft || 999
      return days > 3 && days <= 7
    })
    
    if (soonExpiringItems.length > 0) {
      suggestions.push({
        id: 'waste-3',
        title: '⏰ Plan Ahead', 
        items: soonExpiringItems.slice(0, 3),
        reason: `${soonExpiringItems.length} items expiring this week`,
        priority: 'medium',
        recipes: [
          'Weekly Meal Prep',
          'Make-Ahead Dishes'
        ]
      })
    }

    return suggestions
  }

  const wasteReductionSuggestions = generateWasteReductionSuggestions()

  const generateShoppingListFromMealPlan = async () => {
    await shoppingApi.generateFromMealPlan()
    const res = await shoppingApi.getAll()
    if (res.success && res.data) setShoppingList(res.data)
  }

  const toggleShoppingItem = async (id: string) => {
    await shoppingApi.toggle(id)
    const res = await shoppingApi.getAll()
    if (res.success && res.data) setShoppingList(res.data)
  }

  const addMealPlan = async (mealPlan: Omit<MealPlan, "id">) => {
    const res = await mealPlanApi.create(mealPlan)
    if (res.success && res.data) {
      setMealPlans((prev) => [...prev, res.data!])
    }
  }

  const handlePhotoCapture = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = async (e) => {
        const img = e.target?.result as string
        setMealPhoto(img)
        try {
          const res = await aiApi.classifyPhoto(img)
          if (res.success && res.data) {
            setIngredientSelections(res.data)
            return
          }
        } catch (err) {
          // ignore and fallback
        }
        // Fallback: choose first few inventory items
        const fallback = inventory.slice(0, 3).map((item) => ({
          itemId: item.id,
          itemName: item.name,
          availableQuantity: Number(item.quantity) || 1,
          selectedQuantity: 0,
          unit: item.unit,
        }))
        setIngredientSelections(fallback)
      }
      reader.readAsDataURL(file)
    }
  }

  const updateIngredientQuantity = (itemId: string, quantity: number) => {
    setIngredientSelections((prev) =>
      prev.map((item) => 
        item.itemId === itemId 
          ? { ...item, selectedQuantity: quantity } 
          : item
      )
    )
  }

  const addExtraIngredient = () => {
    setExtraIngredients((prev) => [...prev, { name: '', quantity: '', unit: 'pcs' }])
  }

  const updateExtraIngredient = (index: number, field: 'name' | 'quantity' | 'unit', value: string | number) => {
    setExtraIngredients((prev) =>
      prev.map((item, i) =>
        i === index ? { ...item, [field]: value } : item
      )
    )
  }

  const saveMealRecord = () => {
    if (!selectedRecorderMember) {
      toast({
        title: "Error",
        description: "Please select a family member",
        variant: "destructive",
      })
      return
    }

    const member = familyMembers.find(m => m.id === selectedRecorderMember)
    if (!member) return

    const newMealRecord: MealRecord = {
      id: Date.now().toString(),
      memberId: selectedRecorderMember,
      memberName: member.name,
      mealName,
      photo: mealPhoto,
      ingredients: ingredientSelections
        .filter((item) => item.selectedQuantity > 0)
        .map(({ itemId, itemName, selectedQuantity, unit }) => ({
          itemId,
          itemName,
          quantity: selectedQuantity,
          unit
        })),
      extraIngredients: extraIngredients
        .filter((item) => item.name && item.quantity && parseFloat(item.quantity) > 0)
        .map(({ name, quantity, unit }) => ({
          name,
          quantity: parseFloat(quantity).toString(),
          unit
        })),
      mealType,
      date: new Date().toISOString().split("T")[0],
      time: new Date().toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" }),
    }

    // Update inventory quantities
    const updatedInventory = inventory.map((item) => {
      const usedIngredient = ingredientSelections.find((ing) => ing.itemId === item.id)
      if (usedIngredient && usedIngredient.selectedQuantity > 0) {
        const currentQty = parseFloat(item.quantity) || 0
        const newQty = Math.max(0, currentQty - usedIngredient.selectedQuantity)
        return { ...item, quantity: newQty.toString() }
      }
      return item
    })
    setInventory(updatedInventory)

    // Add to consumption history
    const newConsumptionEntries = ingredientSelections
      .filter((item) => item.selectedQuantity > 0)
      .map((item) => ({
        id: `${Date.now()}-${item.itemId}`,
        memberId: selectedRecorderMember,
        memberName: member.name,
        itemName: item.itemName,
        quantity: item.selectedQuantity,
        date: new Date().toISOString().split("T")[0],
        mealType,
        category: "Recorded Meal",
      }))

    setConsumptionHistory((prev) => [...newConsumptionEntries, ...prev])
    setMealRecords((prev) => [newMealRecord, ...prev])

    // Reset form
    setShowMealRecorder(false)
    setMealPhoto("")
    setMealName("")
    setIngredientSelections([])
    setExtraIngredients([])
    setSelectedRecorderMember("")
  }

  const renderFamily = () => (
    <div className="p-6">
      <FamilyDashboard 
        userId="user-123" 
        onFamilyJoined={(family) => {
          console.log('Family joined:', family)
          // Handle family joined event - you can update state here
        }} 
      />
        </div>
  )

  const renderTracking = () => (
    <div className="p-6">
      <TrackingPage 
        familyId="family-123" 
        userId="user-123" 
      />
          </div>
  )

  // Removed broken renderDashboard function - using the correct one below

  const renderDashboard = () => (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between p-6 pb-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-emerald-500 rounded-full flex items-center justify-center">
            <Package className="w-6 h-6 text-white" />
          </div>
          <h1 className="text-xl font-semibold text-gray-900">FreshKeeper</h1>
        </div>
        <Button variant="ghost" size="icon" className="text-gray-400">
          <Settings className="w-5 h-5" />
        </Button>
      </div>

      {/* Status Cards */}
      <div className="px-6 pb-6">
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center">
            <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-2">
              <CheckCircle className="w-6 h-6 text-green-600" />
            </div>
            <div className="text-2xl font-bold text-gray-900">{freshItems.length}</div>
            <div className="text-sm text-gray-500">Fresh</div>
          </div>
          <div className="text-center">
            <div className="w-12 h-12 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-2">
              <Clock className="w-6 h-6 text-yellow-600" />
            </div>
            <div className="text-2xl font-bold text-gray-900">{useSoonItems.length}</div>
            <div className="text-sm text-gray-500">Use Soon</div>
          </div>
          <div className="text-center">
            <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-2">
              <AlertTriangle className="w-6 h-6 text-red-600" />
            </div>
            <div className="text-2xl font-bold text-gray-900">{expiringItems.length}</div>
            <div className="text-sm text-gray-500">Expiring</div>
          </div>
        </div>
      </div>

      {/* Quick Action Buttons */}
      <div className="px-6 pb-6">
        <div className="grid grid-cols-3 gap-3 mb-4">
          <Dialog>
            <DialogTrigger asChild>
              <Button className="bg-emerald-500 hover:bg-emerald-600 text-white h-12 rounded-xl">
                <Scan className="w-5 h-5 mr-2" />
                Scan Item
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Scan Item</DialogTitle>
                <DialogDescription>Scan barcode or add item manually</DialogDescription>
              </DialogHeader>
              <AddItemForm onAdd={addInventoryItem} />
            </DialogContent>
          </Dialog>

          {/* Scan Receipt */}
          <Dialog open={showReceiptDialog} onOpenChange={setShowReceiptDialog}>
            <DialogTrigger asChild>
              <Button className="bg-emerald-100 hover:bg-emerald-200 text-emerald-700 h-12 rounded-xl border border-emerald-200">
                <ReceiptText className="w-5 h-5 mr-2" />
                Scan Receipt
              </Button>
            </DialogTrigger>

          {/* Food Classifier */}
          <Button 
            onClick={() => setShowFoodClassifier(true)}
            className="bg-orange-100 hover:bg-orange-200 text-orange-700 h-12 rounded-xl border border-orange-200"
          >
            <Camera className="w-5 h-5 mr-2" />
            Classify Food
          </Button>
            <DialogContent className="max-w-lg">
              <DialogHeader>
                <DialogTitle>Scan Receipt</DialogTitle>
                <DialogDescription>Upload a photo of your receipt to extract items</DialogDescription>
              </DialogHeader>
              <div className="space-y-4">
                <div className="relative">
                  <input
                    type="file"
                    accept="image/*,.pdf"
                    onChange={(e) => {
                      const file = e.target.files?.[0];
                      if (file) {
                        setReceiptImage("");
                        setReceiptResult(null);
                        handleReceiptUpload(file);
                      }
                    }}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                    id="receipt-upload"
                  />
                  <label
                    htmlFor="receipt-upload"
                    className="flex flex-col items-center justify-center w-full p-8 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors"
                  >
                    <UploadCloud className="w-12 h-12 text-gray-400 mb-2" />
                    <p className="text-sm font-medium text-gray-700">Click to upload receipt</p>
                    <p className="text-xs text-gray-500">Supports: JPG, PNG, PDF, HEIC, WebP</p>
                  </label>
                </div>
                {(receiptImage || receiptFileName) && (
                  <div className="border rounded-lg p-4 bg-gray-50">
                    <div className="flex items-center space-x-3">
                      {receiptImage && receiptImage.startsWith('data:image/svg+xml') ? (
                        <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
                          <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                          </svg>
                        </div>
                      ) : receiptImage ? (
                        <img src={receiptImage} alt="Receipt preview" className="w-12 h-12 rounded-lg object-cover" />
                      ) : (
                        <div className="w-12 h-12 bg-gray-200 rounded-lg flex items-center justify-center">
                          <svg className="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                          </svg>
                        </div>
                      )}
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-900 truncate">{receiptFileName || "Receipt"}</p>
                        <p className="text-xs text-gray-500">{receiptFileType || "Unknown type"}</p>
                      </div>
                    </div>
                  </div>
                )}
                {receiptResult && (
                  <div className="space-y-4">
                    {receiptResult.items && receiptResult.items.length > 0 ? (
                      <div className="space-y-2">
                        <h4 className="font-medium text-gray-900">Parsed Items ({receiptResult.items.length} found)</h4>
                        <div className="max-h-56 overflow-auto space-y-2">
                          {receiptResult.items.map((it, idx) => (
                            <div key={idx} className="flex items-center justify-between p-3 bg-white border rounded-lg">
                              <div className="flex-1">
                                <p className="text-sm font-medium text-gray-900">{it.name}</p>
                                <p className="text-xs text-gray-500">
                                  {it.quantity} {it.unit}
                                  {typeof it.price === "number" ? ` • $${it.price.toFixed(2)}` : ""}
                                </p>
                              </div>
                              <div className="text-xs text-green-600 font-medium">
                                Ready to add
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    ) : receiptImage && (
                      <div className="space-y-4">
                        <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                          <h4 className="font-medium text-yellow-800 mb-2">⚠️ Items Not Automatically Found</h4>
                          <p className="text-sm text-yellow-700 mb-3">
                            Could not automatically identify grocery items from this receipt. 
                            You can review the extracted text below and add items manually.
                          </p>
                        </div>
                        
                        {receiptResult?.rawText && (
                          <div className="space-y-2">
                            <h4 className="font-medium text-gray-900">Extracted Text</h4>
                            <div className="max-h-40 overflow-auto p-3 bg-gray-50 border rounded-lg text-sm text-gray-700">
                              {receiptResult.rawText}
                            </div>
                          </div>
                        )}
                        
                        <div className="space-y-2">
                          <h4 className="font-medium text-gray-900">Manual Entry</h4>
                          <p className="text-sm text-gray-600">Add items from your receipt manually:</p>
                          <Button
                            variant="outline"
                            onClick={() => {
                              setShowReceiptDialog(false)
                              // Open manual add dialog
                              const manualButton = document.querySelector('[data-manual-add]')
                              if (manualButton) (manualButton as HTMLElement).click()
                            }}
                            className="w-full"
                          >
                            <Plus className="w-4 h-4 mr-2" />
                            Add Items Manually
                          </Button>
                        </div>
                      </div>
                    )}
                    
                    <div className="flex justify-end space-x-2 pt-2">
                      <Button 
                        variant="outline" 
                        onClick={() => {
                          setReceiptImage("")
                          setReceiptFileName("")
                          setReceiptFileType("")
                          setReceiptResult(null)
                        }}
                      >
                        Scan Another
                      </Button>
                      {receiptResult?.items && receiptResult.items.length > 0 && (
                        <Button 
                          onClick={() => {
                            setShowReceiptDialog(false)
                            setReceiptImage("")
                            setReceiptFileName("")
                            setReceiptFileType("")
                            setReceiptResult(null)
                          }}
                        >
                          Done
                        </Button>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </DialogContent>
          </Dialog>

          <Dialog>
            <DialogTrigger asChild>
              <Button
                variant="outline"
                className="border-2 border-blue-500 text-blue-500 hover:bg-blue-50 h-12 rounded-xl bg-transparent"
              >
                <Plus className="w-5 h-5 mr-2" />
                Add Manual
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Add Item Manually</DialogTitle>
                <DialogDescription>Add a new item to your inventory</DialogDescription>
              </DialogHeader>
              <AddItemForm onAdd={addInventoryItem} />
            </DialogContent>
          </Dialog>
        </div>

        {/* Mini Action Buttons */}
        <div className="grid grid-cols-4 gap-2">
          <Button
            variant="ghost"
            size="sm"
            className="flex flex-col items-center gap-1 h-16 text-xs"
            onClick={() => setShowInventoryTable(true)}
          >
            <ListChecks className="w-5 h-5 text-emerald-600" />
            <span>Manage</span>
          </Button>
          <Button
            variant="ghost"
            size="sm"
            className="flex flex-col items-center gap-1 h-16 text-xs"
            onClick={() => setShowMealPlanner(true)}
          >
            <Calendar className="w-5 h-5 text-blue-600" />
            <span>Plan</span>
          </Button>
          <Button
            variant="ghost"
            size="sm"
            className="flex flex-col items-center gap-1 h-16 text-xs"
            onClick={() => setShowAnalytics(true)}
          >
            <BarChart3 className="w-5 h-5 text-purple-600" />
            <span>Stats</span>
          </Button>
          <Button
            variant="ghost"
            size="sm"
            className="flex flex-col items-center gap-1 h-16 text-xs"
            onClick={() => generateShoppingListFromMealPlan()}
          >
            <ShoppingBag className="w-5 h-5 text-orange-600" />
            <span>Shop</span>
          </Button>
        </div>
      </div>

      {/* Your Items Section */}
      <div className="flex-1 px-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Your Items</h2>
          <Button variant="ghost" size="sm" className="text-emerald-600" onClick={() => setShowInventoryTable(true)}>
            View All
          </Button>
        </div>

        {inventory.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 text-center">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
              <Package className="w-8 h-8 text-gray-400" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No items yet</h3>
            <p className="text-gray-500 text-sm">Start tracking your groceries by adding your first item.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {inventory.slice(0, 5).map((item) => (
              <div
                key={item.id}
                className="flex items-center justify-between p-4 bg-white rounded-xl border border-gray-100"
              >
                <div className="flex-1">
                  <h3 className="font-medium text-gray-900">{item.name}</h3>
                  <p className="text-sm text-gray-500">
                    {item.quantity} {item.unit} • {item.category}
                  </p>
                  {item.usedQuantity && (
                    <p className="text-xs text-gray-400">
                      Used: {item.usedQuantity} {item.unit}
                    </p>
                  )}
                </div>
                <div className="flex items-center gap-2">
                  <Badge
                    className={cn(
                      "text-xs",
                      item.daysLeft > 3
                        ? "bg-green-100 text-green-700"
                        : item.daysLeft > 0
                          ? "bg-yellow-100 text-yellow-700"
                          : "bg-red-100 text-red-700",
                    )}
                  >
                    {item.daysLeft > 0 ? `${item.daysLeft}d left` : "Expired"}
                  </Badge>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="w-8 h-8"
                    onClick={() => setSelectedInventoryItem(item)}
                  >
                    <Edit className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            ))}
            {inventory.length > 5 && (
              <Button variant="ghost" className="w-full text-emerald-600" onClick={() => setShowInventoryTable(true)}>
                View all {inventory.length} items
              </Button>
            )}
          </div>
        )}
      </div>

      {/* Inventory Management Dialog */}
      <Dialog open={showInventoryTable} onOpenChange={setShowInventoryTable}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Inventory Management</DialogTitle>
            <DialogDescription>Manage all your grocery items</DialogDescription>
          </DialogHeader>
          <InventoryTable
            inventory={inventory}
            onUpdate={updateInventoryItem}
            onDelete={deleteInventoryItem}
            searchTerm={inventorySearchTerm}
            onSearchChange={setInventorySearchTerm}
            filter={inventoryFilter}
            onFilterChange={setInventoryFilter}
          />
        </DialogContent>
      </Dialog>

      {/* Meal Planner Dialog */}
      <Dialog open={showMealPlanner} onOpenChange={setShowMealPlanner}>
        <DialogContent className="max-w-6xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Weekly Meal Planner</DialogTitle>
            <DialogDescription>Plan your meals for the week</DialogDescription>
          </DialogHeader>
          <MealPlanner
            mealPlans={mealPlans}
            recipes={recipes}
            onAddMealPlan={addMealPlan}
            onGenerateShoppingList={generateShoppingListFromMealPlan}
          />
        </DialogContent>
      </Dialog>

      {/* Analytics Dialog */}
      <Dialog open={showAnalytics} onOpenChange={setShowAnalytics}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Analytics & Insights</DialogTitle>
            <DialogDescription>Track your grocery usage and waste reduction</DialogDescription>
          </DialogHeader>
          <AnalyticsDashboard inventory={inventory} recipes={recipes} mealPlans={mealPlans} />
        </DialogContent>
      </Dialog>

      {/* Edit Item Dialog */}
      <Dialog open={!!selectedInventoryItem} onOpenChange={() => setSelectedInventoryItem(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Item</DialogTitle>
            <DialogDescription>Update item details</DialogDescription>
          </DialogHeader>
          {selectedInventoryItem && (
            <EditItemForm
              item={selectedInventoryItem}
              onUpdate={(updates) => {
                updateInventoryItem(selectedInventoryItem.id, updates)
                setSelectedInventoryItem(null)
              }}
              onDelete={() => {
                deleteInventoryItem(selectedInventoryItem.id)
                setSelectedInventoryItem(null)
              }}
            />
          )}
        </DialogContent>
      </Dialog>
    </div>
  )

  const [mealPlan, setMealPlan] = useState<Record<string, Recipe[]>>({
    Monday: [],
    Tuesday: [],
    Wednesday: [],
    Thursday: [],
    Friday: [],
    Saturday: [],
    Sunday: [],
  })

  const daysOfWeek = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

  const addToMealPlan = (day: string, recipe: Recipe) => {
    setMealPlan((prev) => ({
      ...prev,
      [day as keyof typeof prev]: [...(prev[day as keyof typeof prev] || []), recipe],
    }))
  }

  const removeFromMealPlan = (day: string, index: number) => {
    setMealPlan((prev) => {
      const updatedDayPlan = [...prev[day as keyof typeof prev]]
      updatedDayPlan.splice(index, 1)
      return {
        ...prev,
        [day]: updatedDayPlan,
      }
    })
  }

  const recordMeal = () => {
    if (!selectedRecorderMember || !mealName || ingredientSelections.length === 0) {
      toast({
        title: "Missing Information",
        description: "Please select a member, name the meal, and select ingredients.",
        variant: "destructive",
      })
      return
    }

    const member = familyMembers.find(m => m.id === selectedRecorderMember)
    if (!member) return

    const usedIngredients = ingredientSelections.filter(ing => ing.selectedQuantity > 0)
    if (usedIngredients.length === 0) {
      toast({
        title: "No Ingredients Selected",
        description: "Please select at least one ingredient to record.",
        variant: "destructive",
      })
      return
    }

    // Update inventory quantities
    usedIngredients.forEach(ingredient => {
      const inventoryItem = inventory.find(item => item.id === ingredient.itemId)
      if (inventoryItem) {
        const currentQuantity = Number(inventoryItem.quantity) || 0
        const usedQuantity = ingredient.selectedQuantity
        const newQuantity = Math.max(0, currentQuantity - usedQuantity)
        
        updateInventoryItem(ingredient.itemId, {
          quantity: newQuantity.toString(),
          usedQuantity: usedQuantity.toString()
        })
      }
    })

    // Record the meal
    const newMealRecord = {
      id: Date.now().toString(),
      memberId: selectedRecorderMember,
      memberName: member.name,
      mealName,
      mealType: mealType,
      ingredients: usedIngredients,
      date: format(new Date(), "yyyy-MM-dd"),
      time: format(new Date(), "HH:mm"),
      photo: mealPhoto,
      notes: "" // Initialize notes as empty string since mealNotes is undefined
    }

    setMealRecords(prev => [...prev, {
      id: newMealRecord.id,
      memberId: newMealRecord.memberId,
      memberName: newMealRecord.memberName, 
      mealName: newMealRecord.mealName,
      photo: newMealRecord.photo,
      ingredients: newMealRecord.ingredients.map(ing => ({
        itemId: ing.itemId,
        itemName: ing.itemName,
        quantity: ing.selectedQuantity,
        unit: ing.unit
      })),
      extraIngredients: [],
      mealType: newMealRecord.mealType,
      date: newMealRecord.date,
      time: newMealRecord.time
    }])
    
    // Add consumption entries
    usedIngredients.forEach(ingredient => {
      const newEntry: ConsumptionEntry = {
        id: Date.now().toString() + Math.random(),
        memberId: selectedRecorderMember,
        memberName: member.name,
        itemName: ingredient.itemName,
        quantity: ingredient.selectedQuantity,
        date: format(new Date(), "yyyy-MM-dd"),
        mealType: mealType,
        category: inventory.find(item => item.id === ingredient.itemId)?.category || "Other"
      }
      setConsumptionHistory(prev => [newEntry, ...prev])
    })

    // Reset form
    setMealName("")
    setMealPhoto("")
    setIngredientSelections([])
// Remove setMealNotes since it's not defined in state
    setSelectedRecorderMember("")
    setShowMealRecorder(false)

    toast({
      title: "Meal Recorded",
      description: `Successfully recorded ${mealName} for ${member.name}`,
      variant: "default",
    })
  }

  const renderRecipes = () => (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between p-6 pb-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-emerald-500 rounded-full flex items-center justify-center">
            <Package className="w-6 h-6 text-white" />
          </div>
          <h1 className="text-xl font-semibold text-gray-900">FreshKeeper</h1>
        </div>
        <Button variant="ghost" size="icon" className="text-gray-400">
          <Settings className="w-5 h-5" />
        </Button>
      </div>

      {/* Recipe Ideas Section */}
      <div className="px-6 pb-6">
        <div className="flex items-center gap-2 mb-6">
          <Utensils className="w-5 h-5 text-emerald-600" />
          <h2 className="text-lg font-semibold text-gray-900">Recipe Ideas</h2>
        </div>

        {/* Recipe View Toggle */}
        <div className="flex bg-gray-100 rounded-xl p-1 mb-6">
          <Button
            variant={recipeView === "ai" ? "default" : "ghost"}
            className={cn(
              "flex-1 rounded-lg h-10 text-xs",
              recipeView === "ai"
                ? "bg-white text-gray-900 shadow-sm"
                : "bg-transparent text-gray-600 hover:text-gray-900",
            )}
            onClick={() => setRecipeView("ai")}
          >
            <Sparkles className="w-4 h-4 mr-1" />
            AI Chosen
          </Button>
          <Button
            variant={recipeView === "meal-plan" ? "default" : "ghost"}
            className={cn(
              "flex-1 rounded-lg h-10 text-xs",
              recipeView === "meal-plan"
                ? "bg-white text-gray-900 shadow-sm"
                : "bg-transparent text-gray-600 hover:text-gray-900",
            )}
            onClick={() => setRecipeView("meal-plan")}
          >
            <Calendar className="w-4 h-4 mr-1" />
            Meal Plan
          </Button>
          <Button
            variant={recipeView === "all" ? "default" : "ghost"}
            className={cn(
              "flex-1 rounded-lg h-10 text-xs",
              recipeView === "all"
                ? "bg-white text-gray-900 shadow-sm"
                : "bg-transparent text-gray-600 hover:text-gray-900",
            )}
            onClick={() => setRecipeView("all")}
          >
            <BookOpen className="w-4 h-4 mr-1" />
            All Options
          </Button>
        </div>

        {/* AI Insights Card */}
        {recipeView === "ai" && (
          <div className="bg-gradient-to-r from-purple-50 to-purple-100 rounded-xl p-4 mb-6 border border-purple-200">
            <div className="flex items-center gap-2 mb-2">
              <Brain className="w-5 h-5 text-purple-600" />
              <h3 className="font-medium text-purple-900">AI Meal Generator</h3>
            </div>
            {inventory.length === 0 ? (
              <p className="text-purple-700 text-sm mb-3">Add some grocery items to get AI-powered meal suggestions!</p>
            ) : (
              <p className="text-purple-700 text-sm mb-3">Generate personalized meals from your current inventory!</p>
            )}
            <div className="flex items-center justify-between mb-3">
              <span className="text-purple-700 text-sm font-medium">Available Items:</span>
              <span className="text-emerald-600 font-semibold">{inventory.length} items</span>
            </div>
            <Button 
              onClick={() => setShowAIMealGenerator(true)}
              className="w-full bg-purple-600 hover:bg-purple-700 text-white h-10 rounded-lg shadow-sm"
              disabled={inventory.length === 0}
            >
              <Brain className="w-4 h-4 mr-2" />
              Generate AI Meals
            </Button>
          </div>
        )}

        {recipeView === "meal-plan" && (
          <div className="bg-gradient-to-r from-blue-50 to-blue-100 rounded-xl p-4 mb-6 border border-blue-200">
            <div className="flex items-center gap-2 mb-2">
              <Calendar className="w-5 h-5 text-blue-600" />
              <h3 className="font-medium text-blue-900">Weekly Meal Plan</h3>
            </div>
            <p className="text-blue-700 text-sm mb-3">Plan your meals for the week and generate shopping lists!</p>
            <div className="flex items-center justify-between">
              <span className="text-blue-700 text-sm font-medium">Planned Meals:</span>
              <span className="text-emerald-600 font-semibold">{Object.values(mealPlan).flat().length} meals</span>
            </div>
          </div>
        )}
      </div>

      {/* Content Area */}
      <div className="flex-1 px-6">
        {recipeView === "ai" ? (
          // AI Waste-Reduction Recommendations
          wasteReductionSuggestions.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-16 text-center">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-4">
                <Leaf className="w-8 h-8 text-green-600" />
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">Great Job! No Waste Detected</h3>
              <p className="text-gray-500 text-sm max-w-xs">
                Your inventory looks well-managed. Add more items to get waste-prevention suggestions!
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <h3 className="text-base font-medium text-gray-900">♻️ Smart Waste Prevention</h3>
                <span className="text-xs text-green-600 bg-green-50 px-2 py-1 rounded-full">
                  {wasteReductionSuggestions.length} opportunities
                </span>
              </div>
              
              {wasteReductionSuggestions.map((suggestion) => (
                <div key={suggestion.id} className={`rounded-lg border-l-4 p-3 ${
                  suggestion.priority === 'urgent' 
                    ? 'bg-red-50 border-red-400' 
                    : suggestion.priority === 'high'
                    ? 'bg-orange-50 border-orange-400'
                    : 'bg-blue-50 border-blue-400'
                }`}>
                  <div className="flex items-center justify-between mb-2">
                    <h4 className={`font-medium text-sm ${
                      suggestion.priority === 'urgent' 
                        ? 'text-red-800' 
                        : suggestion.priority === 'high'
                        ? 'text-orange-800'
                        : 'text-blue-800'
                    }`}>
                      {suggestion.title}
                    </h4>
                    <button
                      onClick={() => setShowAIMealGenerator(true)}
                      className={`px-2 py-1 text-xs rounded font-medium ${
                        suggestion.priority === 'urgent' 
                          ? 'bg-red-100 text-red-700 hover:bg-red-200' 
                          : suggestion.priority === 'high'
                          ? 'bg-orange-100 text-orange-700 hover:bg-orange-200'
                          : 'bg-blue-100 text-blue-700 hover:bg-blue-200'
                      }`}
                    >
                      Generate
                    </button>
                  </div>
                  
                  {/* Compact Items Display */}
                  <div className="flex flex-wrap gap-1 mb-2">
                    {suggestion.items.slice(0, 2).map((item, index) => (
                      <span key={index} className={`text-xs px-2 py-0.5 rounded-full ${
                        suggestion.priority === 'urgent' 
                          ? 'bg-red-100 text-red-700' 
                          : suggestion.priority === 'high'
                          ? 'bg-orange-100 text-orange-700'
                          : 'bg-blue-100 text-blue-700'
                      }`}>
                        {item.name} ({item.daysLeft}d)
                      </span>
                    ))}
                    {suggestion.items.length > 2 && (
                      <span className="text-xs text-gray-500 px-2 py-0.5">
                        +{suggestion.items.length - 2} more
                      </span>
                    )}
                  </div>
                  
                  {/* Single Recipe Suggestion */}
                  <div className="flex items-center gap-2 text-xs text-gray-600">
                    <ChefHat className="w-3 h-3" />
                    <span>{suggestion.recipes[0]}</span>
                  </div>
                </div>
              ))}
              
              {/* Simplified Quick Action */}
              <div className="bg-purple-50 rounded-lg p-3 border border-purple-200">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium text-purple-800 text-sm">
                      🎯 Get All Recipes
                    </h4>
                    <p className="text-xs text-purple-600">
                      Generate for all priority items
                    </p>
                  </div>
                  <button
                    onClick={() => setShowAIMealGenerator(true)}
                    className="bg-purple-600 text-white px-3 py-1.5 rounded text-xs font-medium hover:bg-purple-700"
                  >
                    Generate All
                  </button>
                </div>
              </div>
            </div>
          )
        ) : recipeView === "meal-plan" ? (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h3 className="text-base font-medium text-gray-900">This Week</h3>
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  const allMeals = Object.values(mealPlan).flat()
                  if (allMeals.length > 0) {
                    generateShoppingListFromMealPlan()
                  }
                }}
                className="text-xs"
              >
                <ShoppingCart className="w-3 h-3 mr-1" />
                Generate List
              </Button>
            </div>

            <div className="space-y-3">
              {daysOfWeek.map((day) => (
                <div key={day} className="bg-white rounded-xl border border-gray-200 p-4">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-medium text-gray-900">{day}</h4>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => {
                        const availableRecipes = recipes.filter((r) =>
                          r.ingredients.some((ing) =>
                            inventory.some((item) => item.name.toLowerCase().includes(ing.toLowerCase())),
                          ),
                        )
                        if (availableRecipes.length > 0) {
                          const randomRecipe = availableRecipes[Math.floor(Math.random() * availableRecipes.length)]
                          addToMealPlan(day, randomRecipe)
                        }
                      }}
                      className="text-xs text-emerald-600 hover:text-emerald-700"
                    >
                      <Plus className="w-3 h-3 mr-1" />
                      Add Meal
                    </Button>
                  </div>

                  {mealPlan[day as keyof typeof mealPlan]?.length > 0 ? (
                    <div className="space-y-2">
                      {mealPlan[day as keyof typeof mealPlan].map((recipe, index) => (
                        <div key={index} className="flex items-center justify-between bg-gray-50 rounded-lg p-3">
                          <div className="flex items-center gap-3">
                            <div className="w-8 h-8 bg-emerald-100 rounded-lg flex items-center justify-center">
                              <Utensils className="w-4 h-4 text-emerald-600" />
                            </div>
                            <div>
                              <p className="font-medium text-gray-900 text-sm">
                                {recipe ? recipe.name || 'Untitled Recipe' : 'Untitled Recipe'}
                              </p>
                              <p className="text-xs text-gray-500">
                                {recipe.cookTime} • {recipe.difficulty}
                              </p>
                            </div>
                          </div>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => removeFromMealPlan(day, index)}
                            className="text-gray-400 hover:text-red-500"
                          >
                            <X className="w-4 h-4" />
                          </Button>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-6">
                      <div className="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-2">
                        <Calendar className="w-6 h-6 text-gray-400" />
                      </div>
                      <p className="text-gray-500 text-sm">No meals planned</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        ) : (
          // All Recipes
          <div>
            {/* Search and Filters */}
            <div className="space-y-4 mb-6">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <Input
                  placeholder="Search recipes..."
                  className="pl-10 rounded-xl border-gray-200 bg-white"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>

              <RecipeFilters filters={recipeFilter} onFiltersChange={setRecipeFilter} />
            </div>

            <div className="space-y-4">
              {recipes
                .filter((recipe) => {
                  const matchesSearch =
                    recipe.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                    recipe.description.toLowerCase().includes(searchTerm.toLowerCase())
                  const matchesCuisine = recipeFilter.cuisine === "all" || recipe.cuisine === recipeFilter.cuisine
                  const matchesDifficulty =
                    recipeFilter.difficulty === "all" || recipe.difficulty === recipeFilter.difficulty
                  const matchesCookTime =
                    recipeFilter.cookTime === "all" ||
                    (recipeFilter.cookTime === "quick" && Number.parseInt(recipe.cookTime) <= 30) ||
                    (recipeFilter.cookTime === "medium" &&
                      Number.parseInt(recipe.cookTime) > 30 &&
                      Number.parseInt(recipe.cookTime) <= 60) ||
                    (recipeFilter.cookTime === "long" && Number.parseInt(recipe.cookTime) > 60)
                  const matchesDietary =
                    recipeFilter.dietary === "all" || recipe.dietaryLabels?.includes(recipeFilter.dietary)

                  return matchesSearch && matchesCuisine && matchesDifficulty && matchesCookTime && matchesDietary
                })
                .map((recipe) => (
                  <RecipeCard
                    key={recipe.id}
                    recipe={recipe}
                    onViewDetails={setSelectedRecipe}
                    onGenerateShoppingList={generateShoppingListFromRecipe}
                  />
                ))}
            </div>
          </div>
        )}

        {/* Recipe Details Dialog */}
        <Dialog open={!!selectedRecipe} onOpenChange={() => setSelectedRecipe(null)}>
          <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
            {selectedRecipe && (
              <RecipeDetails
                recipe={selectedRecipe}
                onGenerateShoppingList={generateShoppingListFromRecipe}
                onAddToMealPlan={(mealPlan) =>
                  addMealPlan({ ...mealPlan, recipeId: selectedRecipe.id, recipeName: selectedRecipe.name })
                }
              />
            )}
          </DialogContent>
        </Dialog>
      </div>
    </div>
  )

  const renderShopping = () => (
    <div className="flex flex-col h-full">
      <div className="p-6 pb-4">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            {shoppingView === "ai" ? (
              <>
                <Brain className="w-6 h-6 text-purple-600" />
                <h1 className="text-xl font-semibold text-gray-900">AI Smart Shopping</h1>
                <Badge variant="outline" className="text-purple-600 border-purple-200 text-xs">
                  <Sparkles className="w-3 h-3 mr-1" />
                  AI Powered
                </Badge>
              </>
            ) : (
              <h1 className="text-xl font-semibold text-gray-900">Shopping List</h1>
            )}
          </div>
          <div className="flex items-center gap-2">
            {shoppingView !== "ai" && (
              <Dialog>
                <DialogTrigger asChild>
                  <Button size="icon" className="bg-emerald-500 hover:bg-emerald-600 rounded-full">
                    <Plus className="w-5 h-5" />
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Add Shopping Item</DialogTitle>
                    <DialogDescription>Add a new item to your shopping list</DialogDescription>
                  </DialogHeader>
                  <AddShoppingItemForm onAdd={addShoppingItem} />
                </DialogContent>
              </Dialog>
            )}
          </div>
        </div>

        {/* View Toggle */}
        <div className="flex bg-gray-100 rounded-xl p-1 mb-4 overflow-x-auto">
          <Button
            variant={shoppingView === "list" ? "default" : "ghost"}
            className={cn(
              "flex-1 rounded-lg h-10 text-xs min-w-fit px-3",
              shoppingView === "list"
                ? "bg-white text-gray-900 shadow-sm"
                : "bg-transparent text-gray-600 hover:text-gray-900",
            )}
            onClick={() => setShoppingView("list")}
          >
            <ListChecks className="w-3 h-3 mr-1" />
            List
          </Button>
          <Button
            variant={shoppingView === "categories" ? "default" : "ghost"}
            className={cn(
              "flex-1 rounded-lg h-10 text-xs min-w-fit px-3",
              shoppingView === "categories"
                ? "bg-white text-gray-900 shadow-sm"
                : "bg-transparent text-gray-600 hover:text-gray-900",
            )}
            onClick={() => setShoppingView("categories")}
          >
            <Filter className="w-3 h-3 mr-1" />
            Categories
          </Button>
          <Button
            variant={shoppingView === "meal-plan" ? "default" : "ghost"}
            className={cn(
              "flex-1 rounded-lg h-10 text-xs min-w-fit px-3",
              shoppingView === "meal-plan"
                ? "bg-white text-gray-900 shadow-sm"
                : "bg-transparent text-gray-600 hover:text-gray-900",
            )}
            onClick={() => setShoppingView("meal-plan")}
          >
            <Calendar className="w-3 h-3 mr-1" />
            Meals
          </Button>
          <Button
            variant={shoppingView === "ai" ? "default" : "ghost"}
            className={cn(
              "flex-1 rounded-lg h-10 text-xs min-w-fit px-3",
              shoppingView === "ai"
                ? "bg-white text-gray-900 shadow-sm"
                : "bg-transparent text-gray-600 hover:text-gray-900",
            )}
            onClick={() => setShoppingView("ai")}
          >
            <Brain className="w-3 h-3 mr-1" />
            AI Smart
          </Button>
        </div>

        {shoppingView !== "ai" && (
          <div className="flex items-center justify-between mb-4">
            <Badge variant="outline" className="text-emerald-600 border-emerald-200">
              {shoppingList.filter((item) => !item.isCompleted).length} items remaining
            </Badge>
            <div className="flex items-center gap-2">
              <Button variant="ghost" size="sm" className="text-emerald-600">
                <Download className="w-4 h-4 mr-1" />
                Export
              </Button>
              <Button variant="ghost" size="sm" className="text-blue-600" onClick={generateShoppingListFromMealPlan}>
                <Zap className="w-4 h-4 mr-1" />
                Auto-Generate
              </Button>
            </div>
          </div>
        )}
      </div>

      <div className="flex-1 px-6">
        {shoppingView === "list" ? (
          <ShoppingListView shoppingList={shoppingList} onToggleItem={toggleShoppingItem} />
        ) : shoppingView === "categories" ? (
          <ShoppingCategoriesView shoppingList={shoppingList} onToggleItem={toggleShoppingItem} />
        ) : shoppingView === "meal-plan" ? (
          <ShoppingMealPlanView
            shoppingList={shoppingList}
            mealPlans={mealPlans}
            recipes={recipes}
            onToggleItem={toggleShoppingItem}
          />
        ) : (
          <AIShoppingView 
            inventory={inventory}
            shoppingList={shoppingList}
            shoppingHistory={[]}
            onUpdateShoppingList={(items) => {
              setShoppingList(prev => [...prev, ...items])
            }}
          />
        )}
      </div>
    </div>
  )

  const renderAlerts = () => (
    <div className="flex flex-col h-full">
      <div className="p-6 pb-4">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-xl font-semibold text-gray-900">Alerts & Settings</h1>
          <Button variant="ghost" size="icon" className="text-gray-400">
            <Settings className="w-5 h-5" />
          </Button>
        </div>
      </div>

      <div className="flex-1 px-6">
        <Tabs defaultValue="alerts" className="w-full">
          <TabsList className="grid w-full grid-cols-2 mb-6">
            <TabsTrigger value="alerts">Active Alerts</TabsTrigger>
            <TabsTrigger value="settings">Notification Settings</TabsTrigger>
          </TabsList>

          <TabsContent value="alerts">
            <AlertsView
              inventory={inventory}
              useSoonItems={useSoonItems}
              expiringItems={expiringItems}
              mealPlans={mealPlans}
              recipes={recipes}
            />
          </TabsContent>

          <TabsContent value="settings">
            <NotificationSettingsView settings={notificationSettings} onSettingsChange={setNotificationSettings} />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col max-w-md mx-auto">
     
      {/* Main Content */}
      <div className="flex-1 overflow-hidden">
        {currentPage === "dashboard" && renderDashboard()}
        {currentPage === "recipes" && renderRecipes()}
        {currentPage === "shopping" && renderShopping()}
        {currentPage === "alerts" && renderAlerts()}
        {currentPage === "family" && renderFamily()}
        {currentPage === "tracking" && renderTracking()}
      </div>

      {/* Food Classifier Modal */}
      {showFoodClassifier && (
        <FoodClassifier 
          onClose={() => setShowFoodClassifier(false)}
          onIngredientsDetected={(ingredients) => {
            // Handle detected ingredients - you can add them to inventory or shopping list
            console.log('Detected ingredients:', ingredients)
            toast({
              title: "Ingredients Detected",
              description: `Found ${ingredients.length} ingredients in your food`,
            })
          }}
        />
      )}

      {/* AI Meal Generator Modal */}
      {showAIMealGenerator && (
        <AIMealGenerator 
          onClose={() => setShowAIMealGenerator(false)}
          currentInventory={inventory}
        />
      )}

      {/* Bottom Navigation */}
      <div className="bg-white border-t border-gray-200 px-6 py-2">
        <div className="flex items-center justify-around">
          {[
            { id: "dashboard", label: "Dashboard", icon: Home },
            { id: "recipes", label: "Recipes", icon: ChefHat },
            { id: "shopping", label: "Shopping", icon: ShoppingCart },
            { id: "family", label: "Family", icon: Users },
            { id: "tracking", label: "Tracking", icon: Calendar },
            { id: "alerts", label: "Alerts", icon: Bell },
          ].map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => setCurrentPage(id as Page)}
              className={cn(
                "flex flex-col items-center gap-1 py-2 px-3 rounded-lg transition-colors",
                currentPage === id ? "text-emerald-600" : "text-gray-400 hover:text-gray-600",
              )}
            >
              <Icon className="w-5 h-5" />
              <span className="text-xs font-medium">{label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Floating Action Button */}
      {currentPage === "dashboard" && (
        <Dialog>
          <DialogTrigger asChild>
            <Button
              size="icon"
              className="fixed bottom-20 right-6 w-14 h-14 bg-emerald-500 hover:bg-emerald-600 rounded-full shadow-lg"
            >
              <Plus className="w-6 h-6" />
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Quick Add</DialogTitle>
              <DialogDescription>Add a new item to your inventory</DialogDescription>
            </DialogHeader>
            <AddItemForm onAdd={addInventoryItem} />
          </DialogContent>
        </Dialog>
      )}
    </div>
  )
}

function AddItemForm({ onAdd }: { onAdd: (item: Omit<InventoryItem, "id" | "daysLeft" | "addedDate">) => void }) {
  const [formData, setFormData] = useState({
    name: "",
    quantity: "",
    unit: "pieces",
    category: "Other",
    expiryDate: "",
    notes: "",
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (formData.name && formData.quantity && formData.expiryDate) {
      onAdd(formData)
      setFormData({ name: "", quantity: "", unit: "pieces", category: "Other", expiryDate: "", notes: "" })
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <Label htmlFor="name">Item Name</Label>
        <Input
          id="name"
          value={formData.name}
          onChange={(e) => setFormData((prev) => ({ ...prev, name: e.target.value }))}
          placeholder="e.g., Bananas"
          className="rounded-xl"
          required
        />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label htmlFor="quantity">Quantity</Label>
          <Input
            id="quantity"
            value={formData.quantity}
            onChange={(e) => setFormData((prev) => ({ ...prev, quantity: e.target.value }))}
            placeholder="e.g., 6"
            className="rounded-xl"
            required
          />
        </div>
        <div>
          <Label htmlFor="unit">Unit</Label>
          <Select value={formData.unit} onValueChange={(value) => setFormData((prev) => ({ ...prev, unit: value }))}>
            <SelectTrigger className="rounded-xl">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="pieces">Pieces</SelectItem>
              <SelectItem value="kg">Kilograms</SelectItem>
              <SelectItem value="g">Grams</SelectItem>
              <SelectItem value="liter">Liters</SelectItem>
              <SelectItem value="ml">Milliliters</SelectItem>
              <SelectItem value="cups">Cups</SelectItem>
              <SelectItem value="tbsp">Tablespoons</SelectItem>
              <SelectItem value="tsp">Teaspoons</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
      <div>
        <Label htmlFor="category">Category</Label>
        <Select
          value={formData.category}
          onValueChange={(value) => setFormData((prev) => ({ ...prev, category: value }))}
        >
          <SelectTrigger className="rounded-xl">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="Fruits">Fruits</SelectItem>
            <SelectItem value="Vegetables">Vegetables</SelectItem>
            <SelectItem value="Dairy">Dairy</SelectItem>
            <SelectItem value="Meat">Meat & Seafood</SelectItem>
            <SelectItem value="Pantry">Pantry</SelectItem>
            <SelectItem value="Frozen">Frozen</SelectItem>
            <SelectItem value="Beverages">Beverages</SelectItem>
            <SelectItem value="Snacks">Snacks</SelectItem>
            <SelectItem value="Baking">Baking</SelectItem>
            <SelectItem value="Other">Other</SelectItem>
          </SelectContent>
        </Select>
      </div>
      <div>
        <Label htmlFor="expiryDate">Expiry Date</Label>
        <Input
          id="expiryDate"
          type="date"
          value={formData.expiryDate}
          onChange={(e) => setFormData((prev) => ({ ...prev, expiryDate: e.target.value }))}
          className="rounded-xl"
          required
        />
      </div>
      <div>
        <Label htmlFor="notes">Notes (Optional)</Label>
        <Textarea
          id="notes"
          value={formData.notes}
          onChange={(e) => setFormData((prev) => ({ ...prev, notes: e.target.value }))}
          placeholder="Any additional notes..."
          className="rounded-xl"
          rows={2}
        />
      </div>
      <Button type="submit" className="w-full bg-emerald-500 hover:bg-emerald-600 rounded-xl">
        Add Item
      </Button>
    </form>
  )
}

function AddShoppingItemForm({ onAdd }: { onAdd: (item: Omit<ShoppingItem, "id" | "addedDate">) => void }) {
  const [formData, setFormData] = useState({
    name: "",
    quantity: "",
    unit: "pieces",
    category: "Other",
    priority: "medium" as "low" | "medium" | "high",
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (formData.name && formData.quantity) {
      onAdd({
        ...formData,
        isCompleted: false,
        source: "manual",
      })
      setFormData({ name: "", quantity: "", unit: "pieces", category: "Other", priority: "medium" })
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <Label htmlFor="name">Item Name</Label>
        <Input
          id="name"
          value={formData.name}
          onChange={(e) => setFormData((prev) => ({ ...prev, name: e.target.value }))}
          placeholder="e.g., Milk"
          className="rounded-xl"
          required
        />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label htmlFor="quantity">Quantity</Label>
          <Input
            id="quantity"
            value={formData.quantity}
            onChange={(e) => setFormData((prev) => ({ ...prev, quantity: e.target.value }))}
            placeholder="e.g., 2"
            className="rounded-xl"
            required
          />
        </div>
        <div>
          <Label htmlFor="unit">Unit</Label>
          <Select value={formData.unit} onValueChange={(value) => setFormData((prev) => ({ ...prev, unit: value }))}>
            <SelectTrigger className="rounded-xl">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="pieces">Pieces</SelectItem>
              <SelectItem value="kg">Kilograms</SelectItem>
              <SelectItem value="g">Grams</SelectItem>
              <SelectItem value="liter">Liters</SelectItem>
              <SelectItem value="ml">Milliliters</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label htmlFor="category">Category</Label>
          <Select
            value={formData.category}
            onValueChange={(value) => setFormData((prev) => ({ ...prev, category: value }))}
          >
            <SelectTrigger className="rounded-xl">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="Fruits">Fruits</SelectItem>
              <SelectItem value="Vegetables">Vegetables</SelectItem>
              <SelectItem value="Dairy">Dairy</SelectItem>
              <SelectItem value="Meat">Meat</SelectItem>
              <SelectItem value="Pantry">Pantry</SelectItem>
              <SelectItem value="Baking">Baking</SelectItem>
              <SelectItem value="Other">Other</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div>
          <Label htmlFor="priority">Priority</Label>
          <Select
            value={formData.priority}
            onValueChange={(value) =>
              setFormData((prev) => ({ ...prev, priority: value as "low" | "medium" | "high" }))
            }
          >
            <SelectTrigger className="rounded-xl">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="low">Low</SelectItem>
              <SelectItem value="medium">Medium</SelectItem>
              <SelectItem value="high">High</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
      <Button type="submit" className="w-full bg-emerald-500 hover:bg-emerald-600 rounded-xl">
        Add to List
      </Button>
    </form>
  )
}

function EditItemForm({
  item,
  onUpdate,
  onDelete,
}: {
  item: InventoryItem
  onUpdate: (updates: Partial<InventoryItem>) => void
  onDelete: () => void
}) {
  const [formData, setFormData] = useState({
    name: item.name,
    quantity: item.quantity,
    unit: item.unit,
    category: item.category,
    expiryDate: item.expiryDate,
    usedQuantity: item.usedQuantity || "",
    notes: item.notes || "",
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onUpdate(formData)
  }

  return (
    <div className="space-y-4">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <Label htmlFor="name">Item Name</Label>
          <Input
            id="name"
            value={formData.name}
            onChange={(e) => setFormData((prev) => ({ ...prev, name: e.target.value }))}
            className="rounded-xl"
            required
          />
        </div>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <Label htmlFor="quantity">Total Quantity</Label>
            <Input
              id="quantity"
              value={formData.quantity}
              onChange={(e) => setFormData((prev) => ({ ...prev, quantity: e.target.value }))}
              className="rounded-xl"
              required
            />
          </div>
          <div>
            <Label htmlFor="usedQuantity">Used Quantity</Label>
            <Input
              id="usedQuantity"
              value={formData.usedQuantity}
              onChange={(e) => setFormData((prev) => ({ ...prev, usedQuantity: e.target.value }))}
              className="rounded-xl"
              placeholder="0"
            />
          </div>
          <div>
            <Label htmlFor="unit">Unit</Label>
            <Select value={formData.unit} onValueChange={(value) => setFormData((prev) => ({ ...prev, unit: value }))}>
              <SelectTrigger className="rounded-xl">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="pieces">Pieces</SelectItem>
                <SelectItem value="kg">Kilograms</SelectItem>
                <SelectItem value="g">Grams</SelectItem>
                <SelectItem value="liter">Liters</SelectItem>
                <SelectItem value="ml">Milliliters</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label htmlFor="category">Category</Label>
            <Select
              value={formData.category}
              onValueChange={(value: string) => setFormData((prev) => ({ ...prev, category: value }))}
            >
              <SelectTrigger className="rounded-xl">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="Fruits">Fruits</SelectItem>
                <SelectItem value="Vegetables">Vegetables</SelectItem>
                <SelectItem value="Dairy">Dairy</SelectItem>
                <SelectItem value="Meat">Meat</SelectItem>
                <SelectItem value="Pantry">Pantry</SelectItem>
                <SelectItem value="Other">Other</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label htmlFor="expiryDate">Expiry Date</Label>
            <Input
              id="expiryDate"
              type="date"
              value={formData.expiryDate}
              onChange={(e) => setFormData((prev) => ({ ...prev, expiryDate: e.target.value }))}
              className="rounded-xl"
              required
            />
          </div>
        </div>
        <div>
          <Label htmlFor="notes">Notes</Label>
          <Textarea
            id="notes"
            value={formData.notes}
            onChange={(e) => setFormData((prev) => ({ ...prev, notes: e.target.value }))}
            className="rounded-xl"
            rows={2}
          />
        </div>
        <div className="flex gap-2">
          <Button type="submit" className="flex-1 bg-emerald-500 hover:bg-emerald-600 rounded-xl">
            Update Item
          </Button>
          <Button type="button" variant="destructive" onClick={onDelete} className="rounded-xl">
            <Trash2 className="w-4 h-4" />
          </Button>
        </div>
      </form>
    </div>
  )
}

function InventoryTable({
  inventory,
  onUpdate,
  onDelete,
  searchTerm,
  onSearchChange,
  filter,
  onFilterChange,
}: {
  inventory: InventoryItem[]
  onUpdate: (id: string, updates: Partial<InventoryItem>) => void
  onDelete: (id: string) => void
  searchTerm: string
  onSearchChange: (term: string) => void
  filter: string
  onFilterChange: (filter: string) => void
}) {
  const filteredInventory = inventory.filter((item) => {
    const matchesSearch = item.name.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesFilter =
      filter === "all" ||
      (filter === "fresh" && item.daysLeft > 3) ||
      (filter === "use-soon" && item.daysLeft <= 3 && item.daysLeft > 0) ||
      (filter === "expired" && item.daysLeft <= 0) ||
      item.category.toLowerCase() === filter.toLowerCase()

    return matchesSearch && matchesFilter
  })

  return (
    <div className="space-y-4">
      {/* Search and Filter */}
      <div className="flex gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
          <Input
            placeholder="Search items..."
            className="pl-10 rounded-xl"
            value={searchTerm}
            onChange={(e) => onSearchChange(e.target.value)}
          />
        </div>
        <Select value={filter} onValueChange={onFilterChange}>
          <SelectTrigger className="w-40 rounded-xl">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Items</SelectItem>
            <SelectItem value="fresh">Fresh</SelectItem>
            <SelectItem value="use-soon">Use Soon</SelectItem>
            <SelectItem value="expired">Expired</SelectItem>
            <SelectItem value="fruits">Fruits</SelectItem>
            <SelectItem value="vegetables">Vegetables</SelectItem>
            <SelectItem value="dairy">Dairy</SelectItem>
            <SelectItem value="meat">Meat</SelectItem>
            <SelectItem value="pantry">Pantry</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Items List */}
      <div className="space-y-2 max-h-96 overflow-y-auto">
        {filteredInventory.map((item) => (
          <div key={item.id} className="flex items-center justify-between p-3 bg-white rounded-lg border">
            <div className="flex-1">
              <h4 className="font-medium text-gray-900">{item.name}</h4>
              <p className="text-sm text-gray-500">
                {item.quantity} {item.unit} • {item.category}
              </p>
              {item.usedQuantity && (
                <p className="text-xs text-gray-400">
                  Used: {item.usedQuantity} {item.unit}
                </p>
              )}
              {item.notes && <p className="text-xs text-gray-600 italic">{item.notes}</p>}
            </div>
            <div className="flex items-center gap-2">
              <Badge
                className={cn(
                  "text-xs",
                  item.daysLeft > 3
                    ? "bg-green-100 text-green-700"
                    : item.daysLeft > 0
                      ? "bg-yellow-100 text-yellow-700"
                      : "bg-red-100 text-red-700",
                )}
              >
                {item.daysLeft > 0 ? `${item.daysLeft}d left` : "Expired"}
              </Badge>
              <Button
                variant="ghost"
                size="icon"
                className="w-8 h-8"
                onClick={() => {
                  const updates = prompt("Update quantity:", item.quantity)
                  if (updates) onUpdate(item.id, { quantity: updates })
                }}
              >
                <Edit className="w-4 h-4" />
              </Button>
              <Button variant="ghost" size="icon" className="w-8 h-8 text-red-500" onClick={() => onDelete(item.id)}>
                <Trash2 className="w-4 h-4" />
              </Button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function RecipeCard({
  recipe,
  onViewDetails,
  onGenerateShoppingList,
}: {
  recipe: Recipe
  onViewDetails: (recipe: Recipe) => void
  onGenerateShoppingList: (recipe: Recipe) => void
}) {
  return (
    <div className="p-4 bg-white rounded-xl border border-gray-100 shadow-sm">
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <h4 className="font-medium text-gray-900">{recipe.name}</h4>
          <p className="text-sm text-gray-600 mt-1 line-clamp-2">{recipe.description}</p>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={() => onViewDetails(recipe)}
          className="text-emerald-600 border-emerald-200 hover:bg-emerald-50 ml-2"
        >
          Choose
        </Button>
      </div>

      <div className="flex items-center gap-4 mb-3 text-xs text-gray-500">
        <span className="flex items-center gap-1">
          <Clock className="w-3 h-3" />
          {recipe.cookTime}min
        </span>
        <span className="flex items-center gap-1">
          <Users className="w-3 h-3" />
          {recipe.servings} servings
        </span>
        <Badge variant="outline" className="text-xs">
          {recipe.difficulty}
        </Badge>
        {recipe.nutritionScore && (
          <div className="flex items-center gap-1">
            <Award className="w-3 h-3 text-green-600" />
            <span className="text-green-600 font-medium">{recipe.nutritionScore}/10</span>
          </div>
        )}
      </div>

      {recipe.dietaryLabels && recipe.dietaryLabels.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-3">
          {recipe.dietaryLabels.map((label) => (
            <Badge key={label} variant="secondary" className="text-xs">
              <Leaf className="w-3 h-3 mr-1" />
              {label}
            </Badge>
          ))}
        </div>
      )}

      {recipe.canMakeWithInventory ? (
        <Badge className="mb-3 bg-emerald-100 text-emerald-700 text-xs">
          <CheckCircle className="w-3 h-3 mr-1" />
          Can make now!
        </Badge>
      ) : (
        recipe.missingIngredients.length > 0 && (
          <div className="mb-3">
            <p className="text-xs text-amber-600">
              Missing: {recipe.missingIngredients.slice(0, 2).join(", ")}
              {recipe.missingIngredients.length > 2 && ` +${recipe.missingIngredients.length - 2} more`}
            </p>
          </div>
        )
      )}

      <div className="flex items-center gap-2">
        <Button variant="outline" size="sm" onClick={() => onViewDetails(recipe)} className="flex-1 rounded-lg">
          <Eye className="w-4 h-4 mr-1" />
          View Recipe
        </Button>
        {recipe.missingIngredients.length > 0 && (
          <Button variant="ghost" size="sm" onClick={() => onGenerateShoppingList(recipe)} className="text-emerald-600">
            <ShoppingCart className="w-4 h-4 mr-1" />
            Add to List
          </Button>
        )}
      </div>
    </div>
  )
}

function RecipeFilters({
  filters,
  onFiltersChange,
}: {
  filters: {
    cuisine: string
    difficulty: string
    cookTime: string
    dietary: string
  }
  onFiltersChange: (filters: any) => void
}) {
  return (
    <div className="grid grid-cols-2 gap-3">
      <Select value={filters.cuisine} onValueChange={(value) => onFiltersChange({ ...filters, cuisine: value })}>
        <SelectTrigger className="rounded-xl">
          <SelectValue placeholder="Cuisine" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All Cuisines</SelectItem>
          <SelectItem value="American">American</SelectItem>
          <SelectItem value="Mediterranean">Mediterranean</SelectItem>
          <SelectItem value="Asian">Asian</SelectItem>
          <SelectItem value="Italian">Italian</SelectItem>
          <SelectItem value="Mexican">Mexican</SelectItem>
        </SelectContent>
      </Select>

      <Select value={filters.difficulty} onValueChange={(value) => onFiltersChange({ ...filters, difficulty: value })}>
        <SelectTrigger className="rounded-xl">
          <SelectValue placeholder="Difficulty" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All Levels</SelectItem>
          <SelectItem value="Easy">Easy</SelectItem>
          <SelectItem value="Medium">Medium</SelectItem>
          <SelectItem value="Hard">Hard</SelectItem>
        </SelectContent>
      </Select>

      <Select value={filters.cookTime} onValueChange={(value) => onFiltersChange({ ...filters, cookTime: value })}>
        <SelectTrigger className="rounded-xl">
          <SelectValue placeholder="Cook Time" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">Any Time</SelectItem>
          <SelectItem value="quick">Quick (≤30 min)</SelectItem>
          <SelectItem value="medium">Medium (30-60 min)</SelectItem>
          <SelectItem value="long">{">"} 60 min</SelectItem>
        </SelectContent>
      </Select>

      <Select value={filters.dietary} onValueChange={(value) => onFiltersChange({ ...filters, dietary: value })}>
        <SelectTrigger className="rounded-xl">
          <SelectValue placeholder="Dietary" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All Diets</SelectItem>
          <SelectItem value="Vegetarian">Vegetarian</SelectItem>
          <SelectItem value="Vegan">Vegan</SelectItem>
          <SelectItem value="Gluten-Free">Gluten-Free</SelectItem>
          <SelectItem value="Dairy-Free">Dairy-Free</SelectItem>
          <SelectItem value="High Protein">High Protein</SelectItem>
        </SelectContent>
      </Select>
    </div>
  )
}

function RecipeDetails({
  recipe,
  onGenerateShoppingList,
  onAddToMealPlan,
}: {
  recipe: Recipe
  onGenerateShoppingList: (recipe: Recipe) => void
  onAddToMealPlan: (mealPlan: Omit<MealPlan, "id" | "recipeId" | "recipeName">) => void
}) {
  const [cookingMode, setCookingMode] = useState(false)
  const [currentStep, setCurrentStep] = useState(0)

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">{recipe.name}</h2>
          <p className="text-gray-600 mt-2">{recipe.description}</p>
        </div>
      </div>

      {/* Recipe Info */}
      <div className="grid grid-cols-4 gap-4">
        <div className="text-center p-3 bg-gray-50 rounded-lg">
          <Clock className="w-5 h-5 mx-auto mb-1 text-gray-600" />
          <p className="text-sm font-medium">{recipe.cookTime} min</p>
          <p className="text-xs text-gray-500">Cook Time</p>
        </div>
        <div className="text-center p-3 bg-gray-50 rounded-lg">
          <Timer className="w-5 h-5 mx-auto mb-1 text-gray-600" />
          <p className="text-sm font-medium">{recipe.prepTime} min</p>
          <p className="text-xs text-gray-500">Prep Time</p>
        </div>
        <div className="text-center p-3 bg-gray-50 rounded-lg">
          <Users className="w-5 h-5 mx-auto mb-1 text-gray-600" />
          <p className="text-sm font-medium">{recipe.servings}</p>
          <p className="text-xs text-gray-500">Servings</p>
        </div>
        <div className="text-center p-3 bg-gray-50 rounded-lg">
          <Star className="w-5 h-5 mx-auto mb-1 text-yellow-500" />
          <p className="text-sm font-medium">{recipe.rating}</p>
          <p className="text-xs text-gray-500">Rating</p>
        </div>
      </div>

      {/* Nutrition Info */}
      {recipe.calories && (
        <div className="p-4 bg-green-50 rounded-lg">
          <h3 className="font-medium text-gray-900 mb-2">Nutrition (per serving)</h3>
          <div className="grid grid-cols-4 gap-4 text-sm">
            <div>
              <p className="font-medium text-gray-900">{recipe.calories}</p>
              <p className="text-gray-600">Calories</p>
            </div>
            <div>
              <p className="font-medium text-gray-900">{recipe.protein}</p>
              <p className="text-gray-600">Protein</p>
            </div>
            <div>
              <p className="font-medium text-gray-900">{recipe.carbs}</p>
              <p className="text-gray-600">Carbs</p>
            </div>
            <div>
              <p className="font-medium text-gray-900">{recipe.fat}</p>
              <p className="text-gray-600">Fat</p>
            </div>
          </div>
        </div>
      )}

      {/* Ingredients */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-3">Ingredients</h3>
        <div className="space-y-2">
          {recipe.ingredients.map((ingredient, index) => (
            <div key={index} className="flex items-center gap-3 p-2 bg-gray-50 rounded-lg">
              <Checkbox className="data-[state=checked]:bg-emerald-500" />
              <span className="text-gray-900">{ingredient}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Instructions */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-lg font-semibold text-gray-900">Instructions</h3>
          <Button variant="outline" size="sm" onClick={() => setCookingMode(!cookingMode)} className="rounded-lg">
            <Play className="w-4 h-4 mr-1" />
            {cookingMode ? "Exit" : "Start"} Cooking Mode
          </Button>
        </div>

        {cookingMode ? (
          <div className="p-6 bg-emerald-50 rounded-lg">
            <div className="flex items-center justify-between mb-4">
              <h4 className="text-lg font-medium">
                Step {currentStep + 1} of {recipe.instructions.length}
              </h4>
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setCurrentStep(Math.max(0, currentStep - 1))}
                  disabled={currentStep === 0}
                >
                  Previous
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setCurrentStep(Math.min(recipe.instructions.length - 1, currentStep + 1))}
                  disabled={currentStep === recipe.instructions.length - 1}
                >
                  Next
                </Button>
              </div>
            </div>
            <p className="text-lg text-gray-900">{recipe.instructions[currentStep]}</p>
          </div>
        ) : (
          <div className="space-y-3">
            {recipe.instructions.map((instruction, index) => (
              <div key={index} className="flex gap-3 p-3 bg-gray-50 rounded-lg">
                <div className="w-6 h-6 bg-emerald-500 text-white rounded-full flex items-center justify-center text-sm font-medium flex-shrink-0">
                  {index + 1}
                </div>
                <p className="text-gray-900">{instruction}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="flex gap-3">
        {recipe.missingIngredients.length > 0 && (
          <Button
            onClick={() => onGenerateShoppingList(recipe)}
            className="flex-1 bg-emerald-500 hover:bg-emerald-600 rounded-lg"
          >
            <ShoppingCart className="w-4 h-4 mr-2" />
            Add Missing Items to Shopping List
          </Button>
        )}
        <Button
          variant="outline"
          onClick={() => {
            const date = prompt("Enter date (YYYY-MM-DD):")
            const mealType = prompt("Enter meal type (breakfast/lunch/dinner/snack):")
            if (date && mealType) {
              onAddToMealPlan({
                date,
                mealType: mealType as "breakfast" | "lunch" | "dinner" | "snack",
                servings: recipe.servings,
              })
            }
          }}
          className="rounded-lg"
        >
          <Calendar className="w-4 h-4 mr-2" />
          Add to Meal Plan
        </Button>
        <Button variant="outline" className="rounded-lg bg-transparent">
          <Share2 className="w-4 h-4 mr-2" />
          Share
        </Button>
      </div>
    </div>
  )
}

function ShoppingListView({
  shoppingList,
  onToggleItem,
}: {
  shoppingList: ShoppingItem[]
  onToggleItem: (id: string) => void
}) {
  if (shoppingList.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
          <ShoppingCart className="w-8 h-8 text-gray-400" />
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">No items in your list</h3>
        <p className="text-gray-500 text-sm">Add items to start building your shopping list.</p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {shoppingList.map((item) => (
        <div
          key={item.id}
          className={cn(
            "flex items-center gap-3 p-4 bg-white rounded-xl border border-gray-100",
            item.isCompleted && "opacity-60",
          )}
        >
          <Checkbox
            checked={item.isCompleted}
            onCheckedChange={() => onToggleItem(item.id)}
            className="data-[state=checked]:bg-emerald-500 data-[state=checked]:border-emerald-500"
          />
          <div className={cn("flex-1", item.isCompleted && "line-through")}>
            <h3 className="font-medium text-gray-900">{item.name}</h3>
            <p className="text-sm text-gray-500">
              {item.quantity} {item.unit}
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="text-xs">
              {item.category}
            </Badge>
            {item.priority && (
              <Badge
                className={cn(
                  "text-xs",
                  item.priority === "high"
                    ? "bg-red-100 text-red-700"
                    : item.priority === "medium"
                      ? "bg-yellow-100 text-yellow-700"
                      : "bg-gray-100 text-gray-700",
                )}
              >
                {item.priority}
              </Badge>
            )}
            {item.source === "recipe" && (
              <Badge variant="secondary" className="text-xs">
                <ChefHat className="w-3 h-3 mr-1" />
                Recipe
              </Badge>
            )}
          </div>
        </div>
      ))}
    </div>
  )
}

function ShoppingCategoriesView({
  shoppingList,
  onToggleItem,
}: {
  shoppingList: ShoppingItem[]
  onToggleItem: (id: string) => void
}) {
  const categories = Array.from(new Set(shoppingList.map((item) => item.category)))

  return (
    <div className="space-y-6">
      {categories.map((category) => {
        const categoryItems = shoppingList.filter((item) => item.category === category)
        const completedCount = categoryItems.filter((item) => item.isCompleted).length

        return (
          <div key={category}>
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-medium text-gray-900">{category}</h3>
              <Badge variant="outline" className="text-xs">
                {completedCount}/{categoryItems.length} done
              </Badge>
            </div>
            <div className="space-y-2">
              {categoryItems.map((item) => (
                <div
                  key={item.id}
                  className={cn(
                    "flex items-center gap-3 p-3 bg-white rounded-lg border border-gray-100",
                    item.isCompleted && "opacity-60",
                  )}
                >
                  <Checkbox
                    checked={item.isCompleted}
                    onCheckedChange={() => onToggleItem(item.id)}
                    className="data-[state=checked]:bg-emerald-500 data-[state=checked]:border-emerald-500"
                  />
                  <div className={cn("flex-1", item.isCompleted && "line-through")}>
                    <h4 className="font-medium text-gray-900">{item.name}</h4>
                    <p className="text-sm text-gray-500">
                      {item.quantity} {item.unit}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )
      })}
    </div>
  )
}

function ShoppingMealPlanView({
  shoppingList,
  mealPlans,
  recipes,
  onToggleItem,
}: {
  shoppingList: ShoppingItem[]
  mealPlans: MealPlan[]
  recipes: Recipe[]
  onToggleItem: (id: string) => void
}) {
  const mealPlanItems = shoppingList.filter((item) => item.source === "meal-plan" || item.source === "recipe")

  return (
    <div className="space-y-4">
      <h3 className="font-medium text-gray-900">Items from Meal Plans</h3>
      {mealPlanItems.length === 0 ? (
        <div className="text-center py-8">
          <p className="text-gray-500">No items from meal plans yet.</p>
          <p className="text-sm text-gray-400 mt-1">Generate shopping list from your meal plans to see items here.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {mealPlanItems.map((item) => (
            <div
              key={item.id}
              className={cn(
                "flex items-center gap-3 p-4 bg-white rounded-xl border border-gray-100",
                item.isCompleted && "opacity-60",
              )}
            >
              <Checkbox
                checked={item.isCompleted}
                onCheckedChange={() => onToggleItem(item.id)}
                className="data-[state=checked]:bg-emerald-500 data-[state=checked]:border-emerald-500"
              />
              <div className={cn("flex-1", item.isCompleted && "line-through")}>
                <h4 className="font-medium text-gray-900">{item.name}</h4>
                <p className="text-sm text-gray-500">
                  {item.quantity} {item.unit}
                </p>
                {item.recipeId && (
                  <p className="text-xs text-blue-600">For: {recipes.find((r) => r.id === item.recipeId)?.name}</p>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

function MealPlanner({
  mealPlans,
  recipes,
  onAddMealPlan,
  onGenerateShoppingList,
}: {
  mealPlans: MealPlan[]
  recipes: Recipe[]
  onAddMealPlan: (mealPlan: Omit<MealPlan, "id">) => void
  onGenerateShoppingList: () => void
}) {
  const weekStart = startOfWeek(new Date())
  const weekDays = Array.from({ length: 7 }, (_, i) => addDays(weekStart, i))

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Weekly Meal Plan</h3>
        <Button onClick={onGenerateShoppingList} className="bg-emerald-500 hover:bg-emerald-600">
          <ShoppingCart className="w-4 h-4 mr-2" />
          Generate Shopping List
        </Button>
      </div>

      <div className="grid grid-cols-1 gap-4">
        {weekDays.map((day) => {
          const dayMeals = mealPlans.filter(
            (plan) => format(parseISO(plan.date), "yyyy-MM-dd") === format(day, "yyyy-MM-dd"),
          )

          return (
            <div key={day.toISOString()} className="p-4 bg-white rounded-lg border">
              <h4 className="font-medium text-gray-900 mb-3">{format(day, "EEEE, MMM d")}</h4>

              <div className="space-y-2">
                {["breakfast", "lunch", "dinner", "snack"].map((mealType) => {
                  const meal = dayMeals.find((m) => m.mealType === mealType)

                  return (
                    <div key={mealType} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                      <span className="text-sm font-medium capitalize">{mealType}</span>
                      {meal ? (
                        <span className="text-sm text-gray-600">{meal.recipeName}</span>
                      ) : (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => {
                            const recipeId = prompt("Enter recipe ID:")
                            const recipeName = recipes.find((r) => r.id === recipeId)?.name
                            if (recipeId && recipeName) {
                              onAddMealPlan({
                                date: format(day, "yyyy-MM-dd"),
                                mealType: mealType as "breakfast" | "lunch" | "dinner" | "snack",
                                recipeId,
                                recipeName,
                                servings: 2,
                              })
                            }
                          }}
                        >
                          <Plus className="w-4 h-4" />
                        </Button>
                      )}
                    </div>
                  )
                })}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

function MealPlanView({
  mealPlans,
  recipes,
}: {
  mealPlans: MealPlan[]
  recipes: Recipe[]
}) {
  const weekStart = startOfWeek(new Date())
  const weekMeals = mealPlans.filter((plan) => {
    const planDate = parseISO(plan.date)
    return planDate >= weekStart && planDate <= addDays(weekStart, 6)
  })

  if (weekMeals.length === 0) {
    return (
      <div className="text-center py-8">
        <Calendar className="w-12 h-12 mx-auto mb-3 text-gray-400" />
        <p className="text-gray-500">No meals planned for this week.</p>
        <p className="text-sm text-gray-400 mt-1">Start planning your meals to see them here.</p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {weekMeals.map((meal) => {
        const recipe = recipes.find((r) => r.id === meal.recipeId)
        return (
          <div key={meal.id} className="p-3 bg-white rounded-lg border">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-medium text-gray-900">{meal.recipeName}</h4>
                <p className="text-sm text-gray-500">
                  {format(parseISO(meal.date), "MMM d")} • {meal.mealType} • {meal.servings} servings
                </p>
              </div>
              {recipe && (
                <div className="flex items-center gap-1 text-xs text-gray-500">
                  <Clock className="w-3 h-3" />
                  {recipe.cookTime}min
                </div>
              )}
            </div>
          </div>
        )
      })}
    </div>
  )
}

function AIShoppingView({
  inventory,
  shoppingList,
  shoppingHistory,
  onUpdateShoppingList,
}: {
  inventory: InventoryItem[]
  shoppingList: ShoppingItem[]
  shoppingHistory: any[]
  onUpdateShoppingList: (items: any[]) => void
}) {
  const [activeTab, setActiveTab] = useState<'predictions' | 'analytics' | 'suggestions'>('predictions')
  const [aiPredictions, setAiPredictions] = useState<any[]>([])
  const [smartSuggestions, setSmartSuggestions] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [lastGenerated, setLastGenerated] = useState<Date | null>(null)

  // Intelligent AI Predictions based on inventory analysis
  const generateIntelligentPredictions = () => {
    setLoading(true)
    
    // Simulate AI processing time
    setTimeout(() => {
      const predictions = []
      const existingItems = new Set(shoppingList.map(item => item.name.toLowerCase()))
      
      // 1. Analyze inventory for low/expiring items
      const lowStockItems = inventory.filter(item => 
        item.quantity < 2 || item.daysLeft <= 3
      ).map(item => ({
        name: item.name,
        category: item.category,
        confidence: 0.9,
        reason: item.daysLeft <= 3 ? 'Expiring soon - replace needed' : 'Running low on stock',
        priority: item.daysLeft <= 1 ? 'high' : 'medium',
        aiGenerated: true
      }))

      // 2. Smart category-based predictions
      const categoryBasedPredictions = []
      const inventoryCategories = [...new Set(inventory.map(item => item.category))]
      
      // Common items that go with existing categories
      const categoryComplement = {
        'Dairy': ['Eggs', 'Butter', 'Yogurt', 'Cheese'],
        'Fruits': ['Bananas', 'Apples', 'Oranges', 'Berries'],
        'Vegetables': ['Onions', 'Garlic', 'Tomatoes', 'Lettuce'],
        'Meat': ['Chicken Breast', 'Ground Beef', 'Fish'],
        'Grains': ['Rice', 'Pasta', 'Bread', 'Oats'],
        'Pantry': ['Olive Oil', 'Salt', 'Black Pepper', 'Spices']
      }

      inventoryCategories.forEach(category => {
        const suggestions = categoryComplement[category] || []
        const existingInCategory = inventory.filter(item => item.category === category)
        
        suggestions.forEach(suggestion => {
          if (!existingItems.has(suggestion.toLowerCase()) && 
              !existingInCategory.some(item => item.name.toLowerCase().includes(suggestion.toLowerCase()))) {
            categoryBasedPredictions.push({
              name: suggestion,
              category: category,
              confidence: 0.7,
              reason: `Complements your ${category.toLowerCase()} items`,
              priority: 'medium',
              aiGenerated: true
            })
          }
        })
      })

      // 3. Seasonal and smart suggestions
      const currentMonth = new Date().getMonth()
      const seasonalItems = []
      
      if (currentMonth >= 8 && currentMonth <= 10) { // Fall
        seasonalItems.push(
          { name: 'Pumpkins', category: 'Vegetables', reason: 'Fall seasonal favorite' },
          { name: 'Sweet Potatoes', category: 'Vegetables', reason: 'Perfect for fall recipes' },
          { name: 'Apples', category: 'Fruits', reason: 'Apple season - fresh and crisp' }
        )
      } else if (currentMonth >= 5 && currentMonth <= 7) { // Summer
        seasonalItems.push(
          { name: 'Watermelon', category: 'Fruits', reason: 'Refreshing summer fruit' },
          { name: 'Corn', category: 'Vegetables', reason: 'Sweet summer corn' },
          { name: 'Tomatoes', category: 'Vegetables', reason: 'Peak tomato season' }
        )
      }

      seasonalItems.forEach(item => {
        if (!existingItems.has(item.name.toLowerCase())) {
          categoryBasedPredictions.push({
            ...item,
            confidence: 0.6,
            priority: 'low',
            aiGenerated: true
          })
        }
      })

      // Combine all predictions and remove duplicates
      const allPredictions = [...lowStockItems, ...categoryBasedPredictions.slice(0, 4)]
      const uniquePredictions = allPredictions.filter((item, index, self) => 
        index === self.findIndex(p => p.name.toLowerCase() === item.name.toLowerCase())
      ).slice(0, 6) // Limit to 6 predictions

      setAiPredictions(uniquePredictions)
      setLastGenerated(new Date())
      setLoading(false)
    }, 1500) // Simulate AI processing time
  }

  // Generate dynamic smart suggestions
  const generateSmartSuggestions = () => {
    const suggestions = []
    const existingItems = new Set([...shoppingList.map(item => item.name.toLowerCase()), ...inventory.map(item => item.name.toLowerCase())])
    
    // Health-focused suggestions
    const healthyItems = [
      { name: 'Greek Yogurt', category: 'Dairy', benefit: 'High protein, probiotics' },
      { name: 'Quinoa', category: 'Grains', benefit: 'Complete protein, fiber' },
      { name: 'Spinach', category: 'Vegetables', benefit: 'Iron, vitamins' },
      { name: 'Almonds', category: 'Snacks', benefit: 'Healthy fats, protein' },
      { name: 'Blueberries', category: 'Fruits', benefit: 'Antioxidants, vitamins' }
    ]

    // Budget-friendly suggestions
    const budgetItems = [
      { name: 'Dried Beans', category: 'Pantry', benefit: 'Cheap protein source' },
      { name: 'Rice', category: 'Grains', benefit: 'Filling, versatile' },
      { name: 'Eggs', category: 'Dairy', benefit: 'Affordable protein' },
      { name: 'Potatoes', category: 'Vegetables', benefit: 'Filling, nutritious' }
    ]

    // Convenience items
    const convenienceItems = [
      { name: 'Pre-cut Vegetables', category: 'Vegetables', benefit: 'Save prep time' },
      { name: 'Rotisserie Chicken', category: 'Meat', benefit: 'Ready-to-eat protein' },
      { name: 'Frozen Berries', category: 'Fruits', benefit: 'Long-lasting, versatile' }
    ]

    // Mix different types of suggestions
    const allSuggestionsPool = [...healthyItems, ...budgetItems, ...convenienceItems]
    const filteredSuggestions = allSuggestionsPool
      .filter(item => !existingItems.has(item.name.toLowerCase()))
      .slice(0, 5)

    setSmartSuggestions(filteredSuggestions)
  }

  // Add prediction to shopping list
  const addPredictionToList = (prediction: any) => {
    const newItem = {
      id: Date.now() + Math.random(),
      name: prediction.name,
      quantity: 1,
      unit: 'pieces',
      category: prediction.category,
      isCompleted: false,
      priority: prediction.priority || 'medium',
      source: 'ai-prediction',
      confidence: prediction.confidence,
      reason: prediction.reason
    }
    
    onUpdateShoppingList([newItem])
    
    // Remove from predictions to avoid duplicates
    setAiPredictions(prev => prev.filter(p => p.name !== prediction.name))
  }

  // Add suggestion to shopping list
  const addSuggestionToList = (suggestion: any) => {
    const newItem = {
      id: Date.now() + Math.random(),
      name: suggestion.name,
      quantity: 1,
      unit: 'pieces',
      category: suggestion.category,
      isCompleted: false,
      priority: 'medium',
      source: 'ai-suggestion'
    }
    
    onUpdateShoppingList([newItem])
    
    // Remove from suggestions
    setSmartSuggestions(prev => prev.filter(s => s.name !== suggestion.name))
  }

  // Initialize suggestions on load
  useEffect(() => {
    generateSmartSuggestions()
  }, [inventory, shoppingList])

  // Get confidence color
  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-600'
    if (confidence >= 0.6) return 'text-yellow-600'
    return 'text-gray-600'
  }

  // Get priority color
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-red-100 text-red-800 border-red-200'
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'low': return 'bg-gray-100 text-gray-800 border-gray-200'
      default: return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  return (
    <div className="space-y-4">
      {/* AI Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Brain className="w-5 h-5 text-purple-600" />
          <h2 className="text-lg font-semibold text-gray-900">AI Smart Shopping</h2>
        </div>
        <Badge variant="outline" className="text-purple-600 border-purple-200">
          <Sparkles className="w-3 h-3 mr-1" />
          AI Powered
        </Badge>
      </div>

      {/* Enhanced AI Interface */}
      <div className="space-y-4">
        {/* Smart Predictions Section */}
        <div className="p-4 bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg border border-purple-100">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <Target className="w-4 h-4 text-purple-600" />
              <h3 className="font-medium text-purple-900">Smart Predictions</h3>
            </div>
            {lastGenerated && (
              <span className="text-xs text-purple-600">
                Updated {new Date().getTime() - lastGenerated.getTime() < 60000 ? 'now' : 'recently'}
              </span>
            )}
          </div>
          
          <p className="text-sm text-purple-700 mb-3">
            AI analyzes your inventory patterns and predicts what you'll need next.
          </p>
          
          <Button 
            onClick={generateIntelligentPredictions} 
            disabled={loading}
            className="w-full bg-purple-600 hover:bg-purple-700 mb-4"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Analyzing Patterns...
              </>
            ) : (
              <>
                <Brain className="w-4 h-4 mr-2" />
                Generate Smart Predictions
              </>
            )}
          </Button>

          {/* Predictions Results */}
          {aiPredictions.length > 0 && (
            <div className="space-y-2">
              <h4 className="text-sm font-medium text-purple-800 mb-2">
                AI Recommendations ({aiPredictions.length} found)
              </h4>
              {aiPredictions.map((prediction, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-white rounded-lg border border-purple-100">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-medium text-gray-900">{prediction.name}</span>
                      <Badge variant="outline" className={getPriorityColor(prediction.priority)} style={{ fontSize: '10px', padding: '1px 4px' }}>
                        {prediction.priority}
                      </Badge>
                    </div>
                    <p className="text-xs text-gray-600 mb-1">{prediction.reason}</p>
                    <div className="flex items-center gap-2 text-xs">
                      <span className="text-gray-500">Category: {prediction.category}</span>
                      <span className={`font-medium ${getConfidenceColor(prediction.confidence)}`}>
                        {Math.round(prediction.confidence * 100)}% confidence
                      </span>
                    </div>
                  </div>
                  <Button 
                    size="sm" 
                    onClick={() => addPredictionToList(prediction)}
                    className="bg-purple-600 hover:bg-purple-700 text-white text-xs px-3 py-1"
                  >
                    <Plus className="w-3 h-3 mr-1" />
                    Add
                  </Button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Enhanced Analytics Section */}
        <div className="p-4 bg-gradient-to-r from-emerald-50 to-green-50 rounded-lg border border-emerald-100">
          <div className="flex items-center gap-2 mb-3">
            <BarChart3 className="w-4 h-4 text-emerald-600" />
            <h3 className="font-medium text-emerald-900">Shopping Intelligence</h3>
          </div>
          <p className="text-sm text-emerald-700 mb-3">
            Real-time insights into your shopping and inventory patterns.
          </p>
          <div className="grid grid-cols-2 gap-3">
            <div className="p-3 bg-white rounded-lg border">
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs font-medium text-gray-600">Shopping List</span>
                <ShoppingCart className="w-3 h-3 text-emerald-600" />
              </div>
              <div className="text-lg font-bold text-emerald-600">{shoppingList.length}</div>
              <div className="text-xs text-gray-500">
                {shoppingList.filter(item => !item.isCompleted).length} pending
              </div>
            </div>
            <div className="p-3 bg-white rounded-lg border">
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs font-medium text-gray-600">Inventory</span>
                <Package className="w-3 h-3 text-blue-600" />
              </div>
              <div className="text-lg font-bold text-blue-600">{inventory.length}</div>
              <div className="text-xs text-gray-500">
                {inventory.filter(item => item.daysLeft <= 3).length} expiring soon
              </div>
            </div>
            <div className="p-3 bg-white rounded-lg border">
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs font-medium text-gray-600">Categories</span>
                <Filter className="w-3 h-3 text-purple-600" />
              </div>
              <div className="text-lg font-bold text-purple-600">
                {new Set([...inventory.map(i => i.category), ...shoppingList.map(s => s.category)]).size}
              </div>
              <div className="text-xs text-gray-500">tracked</div>
            </div>
            <div className="p-3 bg-white rounded-lg border">
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs font-medium text-gray-600">AI Efficiency</span>
                <Brain className="w-3 h-3 text-orange-600" />
              </div>
              <div className="text-lg font-bold text-orange-600">
                {aiPredictions.length > 0 ? '94%' : 'Ready'}
              </div>
              <div className="text-xs text-gray-500">learning</div>
            </div>
          </div>
        </div>

        {/* Enhanced Smart Suggestions */}
        <div className="p-4 bg-gradient-to-r from-orange-50 to-yellow-50 rounded-lg border border-orange-100">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-orange-600" />
              <h3 className="font-medium text-orange-900">Smart Suggestions</h3>
            </div>
            <Button 
              size="sm" 
              variant="ghost" 
              onClick={generateSmartSuggestions}
              className="text-orange-600 hover:bg-orange-100 text-xs px-2 py-1"
            >
              <div className="w-3 h-3 mr-1">🔄</div>
              Refresh
            </Button>
          </div>
          <p className="text-sm text-orange-700 mb-3">
            Personalized recommendations based on your current inventory and shopping patterns.
          </p>
          <div className="space-y-2">
            {smartSuggestions.map((suggestion, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-white rounded-lg border border-orange-100">
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-medium text-gray-900">{suggestion.name}</span>
                    <span className="text-xs text-gray-500">{suggestion.category}</span>
                  </div>
                  <p className="text-xs text-orange-700">{suggestion.benefit}</p>
                </div>
                <Button 
                  size="sm" 
                  variant="outline"
                  onClick={() => addSuggestionToList(suggestion)}
                  className="text-orange-600 hover:bg-orange-50 border-orange-200 text-xs px-3 py-1 ml-2"
                >
                  <Plus className="w-3 h-3 mr-1" />
                  Add
                </Button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

function AnalyticsDashboard({
  inventory,
  recipes,
  mealPlans,
}: {
  inventory: InventoryItem[]
  recipes: Recipe[]
  mealPlans: MealPlan[]
}) {
  const totalItems = inventory.length
  const expiredItems = inventory.filter((item) => item.daysLeft <= 0).length
  const wasteReduction = totalItems > 0 ? Math.round(((totalItems - expiredItems) / totalItems) * 100) : 0
  const favoriteRecipes = recipes.filter((recipe) => recipe.isFavorite).length
  const plannedMeals = mealPlans.length

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-2 gap-4">
        <div className="p-4 bg-emerald-50 rounded-lg">
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp className="w-5 h-5 text-emerald-600" />
            <h3 className="font-medium text-emerald-900">Waste Reduction</h3>
          </div>
          <p className="text-2xl font-bold text-emerald-600">{wasteReduction}%</p>
          <p className="text-sm text-emerald-700">Items saved from expiring</p>
        </div>

        <div className="p-4 bg-blue-50 rounded-lg">
          <div className="flex items-center gap-2 mb-2">
            <Package className="w-5 h-5 text-blue-600" />
            <h3 className="font-medium text-blue-900">Total Items</h3>
          </div>
          <p className="text-2xl font-bold text-blue-600">{totalItems}</p>
          <p className="text-sm text-blue-700">In your inventory</p>
        </div>

        <div className="p-4 bg-purple-50 rounded-lg">
          <div className="flex items-center gap-2 mb-2">
            <Heart className="w-5 h-5 text-purple-600" />
            <h3 className="font-medium text-purple-900">Favorite Recipes</h3>
          </div>
          <p className="text-2xl font-bold text-purple-600">{favoriteRecipes}</p>
          <p className="text-sm text-purple-700">Recipes you love</p>
        </div>

        <div className="p-4 bg-orange-50 rounded-lg">
          <div className="flex items-center gap-2 mb-2">
            <Calendar className="w-5 h-5 text-orange-600" />
            <h3 className="font-medium text-orange-900">Planned Meals</h3>
          </div>
          <p className="text-2xl font-bold text-orange-600">{plannedMeals}</p>
          <p className="text-sm text-orange-700">This week</p>
        </div>
      </div>

      {/* Category Breakdown */}
      <div className="p-4 bg-white rounded-lg border">
        <h3 className="font-medium text-gray-900 mb-3">Inventory by Category</h3>
        <div className="space-y-2">
          {Array.from(new Set(inventory.map((item) => item.category))).map((category) => {
            const categoryItems = inventory.filter((item) => item.category === category)
            const percentage = Math.round((categoryItems.length / totalItems) * 100)

            return (
              <div key={category} className="flex items-center justify-between">
                <span className="text-sm text-gray-600">{category}</span>
                <div className="flex items-center gap-2">
                  <div className="w-20 h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div className="h-full bg-emerald-500 rounded-full" style={{ width: `${percentage}%` }} />
                  </div>
                  <span className="text-sm font-medium text-gray-900">{categoryItems.length}</span>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}

function AlertsView({
  inventory,
  useSoonItems,
  expiringItems,
  mealPlans,
  recipes,
}: {
  inventory: InventoryItem[]
  useSoonItems: InventoryItem[]
  expiringItems: InventoryItem[]
  mealPlans: MealPlan[]
  recipes: Recipe[]
}) {
  return (
    <div className="space-y-6">
      {/* Expiring Items */}
      {useSoonItems.length > 0 || expiringItems.length > 0 ? (
        <div className="space-y-3">
          <h3 className="font-medium text-gray-900">Items Need Attention</h3>
          {[...useSoonItems, ...expiringItems].map((item) => (
            <div
              key={item.id}
              className="flex items-center justify-between p-4 bg-white rounded-xl border border-gray-100"
            >
              <div className="flex items-center gap-3">
                <div className={cn("w-3 h-3 rounded-full", item.daysLeft > 0 ? "bg-yellow-400" : "bg-red-400")} />
                <div>
                  <h4 className="font-medium text-gray-900">{item.name}</h4>
                  <p className="text-sm text-gray-500">
                    {item.quantity} {item.unit} • {item.category}
                  </p>
                </div>
              </div>
              <Badge
                className={cn(
                  "text-xs",
                  item.daysLeft > 0 ? "bg-yellow-100 text-yellow-700" : "bg-red-100 text-red-700",
                )}
              >
                {item.daysLeft > 0 ? `${item.daysLeft}d left` : "Expired"}
              </Badge>
            </div>
          ))}
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-4">
            <CheckCircle className="w-8 h-8 text-green-500" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">All items are fresh!</h3>
          <p className="text-gray-500 text-sm">No items need immediate attention.</p>
        </div>
      )}

      {/* Smart Reminders */}
      <div className="space-y-3">
        <h3 className="font-medium text-gray-900">Smart Reminders</h3>
        <div className="space-y-2">
          <div className="flex items-center gap-3 p-3 bg-blue-50 rounded-lg">
            <Bell className="w-5 h-5 text-blue-600" />
            <div>
              <p className="text-sm font-medium text-blue-900">Weekly Shopping</p>
              <p className="text-xs text-blue-700">Plan your shopping for this weekend</p>
            </div>
          </div>
          <div className="flex items-center gap-3 p-3 bg-purple-50 rounded-lg">
            <Calendar className="w-5 h-5 text-purple-600" />
            <div>
              <p className="text-sm font-medium text-purple-900">Meal Prep Sunday</p>
              <p className="text-xs text-purple-700">Prepare meals for the upcoming week</p>
            </div>
          </div>
          <div className="flex items-center gap-3 p-3 bg-green-50 rounded-lg">
            <Target className="w-5 h-5 text-green-600" />
            <div>
              <p className="text-sm font-medium text-green-900">Inventory Check</p>
              <p className="text-xs text-green-700">Review and update your inventory</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function NotificationSettingsView({
  settings,
  onSettingsChange,
}: {
  settings: NotificationSettings
  onSettingsChange: (settings: NotificationSettings) => void
}) {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="font-medium text-gray-900 mb-4">Notification Preferences</h3>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-gray-900">Expiry Alerts</p>
              <p className="text-sm text-gray-500">Get notified when items are about to expire</p>
            </div>
            <Switch
              checked={settings.expiryAlerts}
              onCheckedChange={(checked) => onSettingsChange({ ...settings, expiryAlerts: checked })}
            />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-gray-900">Meal Plan Reminders</p>
              <p className="text-sm text-gray-500">Reminders for planned meals</p>
            </div>
            <Switch
              checked={settings.mealPlanReminders}
              onCheckedChange={(checked) => onSettingsChange({ ...settings, mealPlanReminders: checked })}
            />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-gray-900">Shopping Reminders</p>
              <p className="text-sm text-gray-500">Weekly shopping list reminders</p>
            </div>
            <Switch
              checked={settings.shoppingReminders}
              onCheckedChange={(checked) => onSettingsChange({ ...settings, shoppingReminders: checked })}
            />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-gray-900">Waste Reduction Tips</p>
              <p className="text-sm text-gray-500">Tips to reduce food waste</p>
            </div>
            <Switch
              checked={settings.wasteReductionTips}
              onCheckedChange={(checked) => onSettingsChange({ ...settings, wasteReductionTips: checked })}
            />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-gray-900">Email Notifications</p>
              <p className="text-sm text-gray-500">Receive notifications via email</p>
            </div>
            <Switch
              checked={settings.emailNotifications}
              onCheckedChange={(checked) => onSettingsChange({ ...settings, emailNotifications: checked })}
            />
          </div>
        </div>
      </div>

      <div className="pt-4 border-t">
        <Button className="w-full bg-emerald-500 hover:bg-emerald-600 rounded-xl">Save Notification Settings</Button>
      </div>
    </div>
  )
}
