import type {
  InventoryItem,
  Recipe,
  ShoppingItem,
  MealPlan,
  NotificationSettings,
  ApiResponse,
  CreateInventoryItemRequest,
  UpdateInventoryItemRequest,
  CreateShoppingItemRequest,
  CreateMealPlanRequest,
  RecipeFilterRequest,
} from "./types"

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "/api"

// Generic API call function
async function apiCall<T>(endpoint: string, options: RequestInit = {}): Promise<ApiResponse<T>> {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      ...options,
    })

    // Check if response is JSON
    const contentType = response.headers.get('content-type')
    let data
    
    try {
      if (contentType && contentType.includes('application/json')) {
        data = await response.json()
      } else {
        // If not JSON, get text and create error
        const text = await response.text()
        console.error('Server returned non-JSON response:', text.substring(0, 200))
        return {
          success: false,
          error: `Server error (${response.status}): ${response.statusText}`,
        }
      }
    } catch (jsonError) {
      // Handle JSON parsing errors
      const text = await response.text()
      console.error('Failed to parse JSON response:', text.substring(0, 200))
      return {
        success: false,
        error: `Invalid server response (${response.status}): ${response.statusText}`,
      }
    }

    if (!response.ok) {
      return {
        success: false,
        error: data.error || `Server error (${response.status}): ${response.statusText}`,
      }
    }

    return {
      success: true,
      data: data.data || data,
    }
  } catch (error) {
    console.error('Network/API error:', error)
    
    // Handle specific network errors
    let errorMessage = "Network error"
    if (error instanceof Error) {
      if (error.message.includes('fetch')) {
        errorMessage = "Network connection failed. Please check your internet connection."
      } else if (error.message.includes('CORS')) {
        errorMessage = "CORS error - server configuration issue"
      } else if (error.message.includes('timeout')) {
        errorMessage = "Request timeout - server may be overloaded"
      } else {
        errorMessage = error.message
      }
    }
    
    return {
      success: false,
      error: errorMessage,
    }
  }
}

// Inventory API functions
export const inventoryApi = {
  getAll: () => apiCall<InventoryItem[]>("/inventory"),

  create: (item: CreateInventoryItemRequest) =>
    apiCall<InventoryItem>("/inventory", {
      method: "POST",
      body: JSON.stringify(item),
    }),

  update: (id: string, updates: UpdateInventoryItemRequest) =>
    apiCall<InventoryItem>(`/inventory/${id}`, {
      method: "PUT",
      body: JSON.stringify(updates),
    }),

  delete: (id: string) =>
    apiCall<void>(`/inventory/${id}`, {
      method: "DELETE",
    }),

  search: (term: string, filter?: string) =>
    apiCall<InventoryItem[]>(`/inventory/search?q=${term}&filter=${filter || "all"}`),
}

// Recipe API functions
export const recipeApi = {
  getAll: (filters?: RecipeFilterRequest) => {
    const params = new URLSearchParams()
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value && value !== "all") {
          params.append(key, value.toString())
        }
      })
    }
    return apiCall<Recipe[]>(`/recipes?${params.toString()}`)
  },

  getById: (id: string) => apiCall<Recipe>(`/recipes/${id}`),

  getAiSuggestions: () => apiCall<Recipe[]>("/recipes/ai-suggestions"),

  toggleFavorite: (id: string) =>
    apiCall<Recipe>(`/recipes/${id}/favorite`, {
      method: "POST",
    }),

  rate: (id: string, rating: number) =>
    apiCall<Recipe>(`/recipes/${id}/rate`, {
      method: "POST",
      body: JSON.stringify({ rating }),
    }),
}

// Shopping List API functions
export const shoppingApi = {
  getAll: () => apiCall<ShoppingItem[]>("/shopping"),

  create: (item: CreateShoppingItemRequest) =>
    apiCall<ShoppingItem>("/shopping", {
      method: "POST",
      body: JSON.stringify(item),
    }),

  toggle: (id: string) =>
    apiCall<ShoppingItem>(`/shopping/${id}/toggle`, {
      method: "POST",
    }),

  delete: (id: string) =>
    apiCall<void>(`/shopping/${id}`, {
      method: "DELETE",
    }),

  generateFromRecipe: (recipeId: string) =>
    apiCall<ShoppingItem[]>(`/shopping/generate/recipe/${recipeId}`, {
      method: "POST",
    }),

  generateFromMealPlan: () =>
    apiCall<ShoppingItem[]>("/shopping/generate/meal-plan", {
      method: "POST",
    }),

  generateAuto: () =>
    apiCall<ShoppingItem[]>("/shopping/generate/auto", {
      method: "POST",
    }),

  categorize: () =>
    apiCall<{ groups: Record<string, ShoppingItem[]> }>("/shopping/categorize", {
      method: "POST",
    }),

  export: () => apiCall<string>("/shopping/export"),

  aiOptimize: () =>
    apiCall<ShoppingItem[]>("/shopping/ai-optimize", {
      method: "POST",
    }),
}

// Meal Plan API functions
export const mealPlanApi = {
  getAll: () => apiCall<MealPlan[]>("/meal-plans"),

  create: (mealPlan: CreateMealPlanRequest) =>
    apiCall<MealPlan>("/meal-plans", {
      method: "POST",
      body: JSON.stringify(mealPlan),
    }),

  delete: (id: string) =>
    apiCall<void>(`/meal-plans/${id}`, {
      method: "DELETE",
    }),

  getWeekly: (startDate: string) => apiCall<MealPlan[]>(`/meal-plans/weekly?start=${startDate}`),

  aiGenerate: (params?: { startDate?: string; save?: boolean; servings?: number }) =>
    apiCall<Omit<MealPlan, "id">[]>("/meal-plans/ai-generate", {
      method: "POST",
      body: JSON.stringify(params || {}),
    }),
}

// Notifications API functions
export const notificationsApi = {
  getSettings: () => apiCall<NotificationSettings>("/notifications/settings"),

  updateSettings: (settings: Partial<NotificationSettings>) =>
    apiCall<NotificationSettings>("/notifications/settings", {
      method: "PUT",
      body: JSON.stringify(settings),
    }),

  getAlerts: () =>
    apiCall<{
      expiring: InventoryItem[]
      reminders: string[]
    }>("/notifications/alerts"),
}

// Analytics API functions
export const analyticsApi = {
  getStats: () =>
    apiCall<{
      totalItems: number
      wasteReduction: number
      moneySaved: number
      recipesCooked: number
      favoriteCategories: string[]
      monthlyTrends: Array<{ month: string; waste: number; savings: number }>
    }>("/analytics/stats"),

  getWasteReport: () =>
    apiCall<{
      totalWaste: number
      wasteByCategory: Array<{ category: string; amount: number }>
      suggestions: string[]
    }>("/analytics/waste"),
}

// AI API functions
export const aiApi = {
  classifyPhoto: (imageDataUrl: string) =>
    apiCall<Array<{ itemId: string; itemName: string; availableQuantity: number; selectedQuantity: number; unit: string }>>(
      "/ai/classify-photo",
      {
        method: "POST",
        body: JSON.stringify({ imageDataUrl }),
      },
    ),

  expiryEstimate: (params: { imageDataUrl?: string; itemName?: string; condition?: string }) =>
    apiCall<{ daysLeft: number; notes?: string }>("/ai/expiry-estimate", {
      method: "POST",
      body: JSON.stringify(params),
    }),

  extractMeal: (params: { imageDataUrl?: string; notes?: string; deduct?: boolean; addMissingToShopping?: boolean }) =>
    apiCall<Array<{ name: string; quantity: number; unit: string }>>("/ai/extract-meal", {
      method: "POST",
      body: JSON.stringify(params),
    }),
}

// OCR API functions
export const ocrApi = {
  receipt: (imageDataUrl: string) =>
    apiCall<{ items: Array<{ name: string; quantity: string; unit: string; price?: number; date?: string }>; purchaseDate?: string }>(
      "/ocr/receipt",
      {
        method: "POST",
        body: JSON.stringify({ imageDataUrl }),
      },
    ),
}
