import type { FamilyMeal, FamilyMealIngredient, FamilyMealNotification, NotificationPreferences } from './types'

export class FamilyMealService {
  private static meals: Map<string, FamilyMeal> = new Map()
  private static notifications: Map<string, FamilyMealNotification> = new Map()
  private static preferences: Map<string, NotificationPreferences> = new Map()

  /**
   * Create a new family meal
   */
  static async createFamilyMeal(
    familyId: string,
    name: string,
    description: string,
    date: string,
    time: string,
    createdBy: string,
    ingredients: Omit<FamilyMealIngredient, 'id'>[]
  ): Promise<FamilyMeal> {
    const mealId = `meal_${Date.now()}_${Math.random().toString(36).substring(2, 8)}`
    
    const meal: FamilyMeal = {
      id: mealId,
      familyId,
      name,
      description,
      date,
      time,
      createdBy,
      participants: [createdBy], // Creator is automatically a participant
      ingredients: ingredients.map(ing => ({
        ...ing,
        id: `ingredient_${Date.now()}_${Math.random().toString(36).substring(2, 6)}`
      })),
      status: 'planned',
      notifications: [],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }

    this.meals.set(mealId, meal)
    return meal
  }

  /**
   * Get family meals
   */
  static async getFamilyMeals(familyId: string): Promise<FamilyMeal[]> {
    const allMeals = Array.from(this.meals.values())
    return allMeals.filter(meal => meal.familyId === familyId)
  }

  /**
   * Get upcoming meals
   */
  static async getUpcomingMeals(familyId: string): Promise<FamilyMeal[]> {
    const meals = await this.getFamilyMeals(familyId)
    const now = new Date()
    
    return meals
      .filter(meal => new Date(`${meal.date}T${meal.time}`) > now)
      .sort((a, b) => new Date(`${a.date}T${a.time}`).getTime() - new Date(`${b.date}T${b.time}`).getTime())
  }

  /**
   * Update meal status
   */
  static async updateMealStatus(mealId: string, status: FamilyMeal['status']): Promise<FamilyMeal | null> {
    const meal = this.meals.get(mealId)
    if (!meal) return null

    meal.status = status
    meal.updatedAt = new Date().toISOString()
    this.meals.set(mealId, meal)
    return meal
  }

  /**
   * Add participant to meal
   */
  static async addParticipant(mealId: string, userId: string): Promise<boolean> {
    const meal = this.meals.get(mealId)
    if (!meal) return false

    if (!meal.participants.includes(userId)) {
      meal.participants.push(userId)
      meal.updatedAt = new Date().toISOString()
      this.meals.set(mealId, meal)
    }
    return true
  }

  /**
   * Create notification for meal
   */
  static async createMealNotification(
    mealId: string,
    type: 'app' | 'whatsapp' | 'email' | 'all',
    recipients: string[],
    scheduledFor: string,
    message: string
  ): Promise<FamilyMealNotification> {
    const notificationId = `notif_${Date.now()}_${Math.random().toString(36).substring(2, 6)}`
    
    const notification: FamilyMealNotification = {
      id: notificationId,
      mealId,
      type,
      recipients,
      scheduledFor,
      message,
      sent: false
    }

    this.notifications.set(notificationId, notification)
    
    // Add to meal's notifications
    const meal = this.meals.get(mealId)
    if (meal) {
      meal.notifications.push(notification)
      this.meals.set(mealId, meal)
    }

    return notification
  }

  /**
   * Get user notification preferences
   */
  static async getNotificationPreferences(userId: string): Promise<NotificationPreferences | null> {
    return this.preferences.get(userId) || null
  }

  /**
   * Update notification preferences
   */
  static async updateNotificationPreferences(
    userId: string,
    preferences: Partial<NotificationPreferences>
  ): Promise<NotificationPreferences> {
    const existing = this.preferences.get(userId)
    
    const updated: NotificationPreferences = {
      id: `pref_${userId}`,
      userId,
      familyId: preferences.familyId,
      appNotifications: preferences.appNotifications ?? true,
      whatsappNotifications: preferences.whatsappNotifications ?? false,
      emailNotifications: preferences.emailNotifications ?? true,
      mealReminders: preferences.mealReminders ?? true,
      shoppingReminders: preferences.shoppingReminders ?? true,
      expiryAlerts: preferences.expiryAlerts ?? true,
      whatsappNumber: preferences.whatsappNumber,
      emailAddress: preferences.emailAddress,
      reminderTiming: {
        meals: preferences.reminderTiming?.meals ?? 30,
        shopping: preferences.reminderTiming?.shopping ?? 2,
        expiry: preferences.reminderTiming?.expiry ?? 1
      }
    }

    this.preferences.set(userId, updated)
    return updated
  }

  /**
   * Send notification (mock implementation)
   */
  static async sendNotification(notificationId: string): Promise<boolean> {
    const notification = this.notifications.get(notificationId)
    if (!notification) return false

    // Mock sending - in real implementation, this would integrate with:
    // - Push notification service for app notifications
    // - WhatsApp Business API
    // - Email service (SendGrid, AWS SES, etc.)
    
    console.log(`Sending ${notification.type} notification:`, notification.message)
    
    notification.sent = true
    notification.sentAt = new Date().toISOString()
    this.notifications.set(notificationId, notification)
    
    return true
  }
}
