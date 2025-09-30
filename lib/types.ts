export interface InventoryItem {
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
  userId?: string
}

export interface Recipe {
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
  userId?: string
}

export interface ShoppingItem {
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
  userId?: string
}

export interface MealPlan {
  id: string
  date: string
  mealType: "breakfast" | "lunch" | "dinner" | "snack"
  recipeId: string
  recipeName: string
  servings: number
  userId?: string
}

export interface NotificationSettings {
  id?: string
  expiryAlerts: boolean
  mealPlanReminders: boolean
  shoppingReminders: boolean
  wasteReductionTips: boolean
  emailNotifications: boolean
  userId?: string
}

export interface User {
  id: string
  email: string
  name: string
  createdAt: string
  updatedAt: string
  familyId?: string
  role?: 'admin' | 'member'
  avatar?: string
}

// Family Management Types
export interface Family {
  id: string
  name: string
  createdBy: string
  createdAt: string
  inviteCode: string
  qrCode: string
  members: FamilyMember[]
  isActive: boolean
}

export interface FamilyMember {
  id: string
  familyId: string
  userId: string
  name: string
  email: string
  role: 'admin' | 'member'
  joinedAt: string
  isActive: boolean
  avatar?: string
}

export interface FamilySyncData {
  familyId: string
  inventory: InventoryItem[]
  mealPlans: MealPlan[]
  shoppingLists: ShoppingItem[]
  lastSync: string
  syncStatus: 'synced' | 'pending' | 'error'
}

export interface FamilyInvite {
  id: string
  familyId: string
  inviteCode: string
  qrCode: string
  createdBy: string
  expiresAt: string
  maxUses?: number
  usedCount: number
  isActive: boolean
}

// Family Meal and Tracking Types
export interface FamilyMeal {
  id: string
  familyId: string
  name: string
  description: string
  date: string
  time: string
  createdBy: string
  participants: string[] // user IDs
  ingredients: FamilyMealIngredient[]
  status: 'planned' | 'cooking' | 'completed' | 'cancelled'
  notifications: FamilyMealNotification[]
  createdAt: string
  updatedAt: string
}

export interface FamilyMealIngredient {
  id: string
  name: string
  quantity: string
  unit: string
  category: string
  isAvailable: boolean
  needsShopping: boolean
}

export interface FamilyMealNotification {
  id: string
  mealId: string
  type: 'app' | 'whatsapp' | 'email' | 'all'
  recipients: string[] // user IDs
  scheduledFor: string
  message: string
  sent: boolean
  sentAt?: string
}

export interface NotificationPreferences {
  id: string
  userId: string
  familyId?: string
  appNotifications: boolean
  whatsappNotifications: boolean
  emailNotifications: boolean
  mealReminders: boolean
  shoppingReminders: boolean
  expiryAlerts: boolean
  whatsappNumber?: string
  emailAddress?: string
  reminderTiming: {
    meals: number // minutes before
    shopping: number // hours before
    expiry: number // days before
  }
}

export interface TrackingPageData {
  familyMeals: FamilyMeal[]
  upcomingMeals: FamilyMeal[]
  recentMeals: FamilyMeal[]
  notificationStats: {
    totalSent: number
    appNotifications: number
    whatsappNotifications: number
    emailNotifications: number
  }
}

// API Response types
export interface ApiResponse<T> {
  success: boolean
  data?: T
  error?: string
  message?: string
}

// API Request types
export interface CreateInventoryItemRequest {
  name: string
  quantity: string
  unit: string
  category: string
  expiryDate: string
  notes?: string
}

export interface UpdateInventoryItemRequest extends Partial<CreateInventoryItemRequest> {
  usedQuantity?: string
}

export interface CreateShoppingItemRequest {
  name: string
  category: string
  quantity: string
  unit: string
  source: "manual" | "recipe" | "meal-plan"
  recipeId?: string
  priority?: "low" | "medium" | "high"
}

export interface CreateMealPlanRequest {
  date: string
  mealType: "breakfast" | "lunch" | "dinner" | "snack"
  recipeId: string
  recipeName: string
  servings: number
}

export interface RecipeFilterRequest {
  cuisine?: string
  difficulty?: string
  cookTime?: string
  dietary?: string
  search?: string
  canMakeWithInventory?: boolean
}

export interface PurchasedItem {
  id: string
  name: string
  quantity: string
  unit: string
  price?: number
  purchasedAt: string
  userId?: string
}
