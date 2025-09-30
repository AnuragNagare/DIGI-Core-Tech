'use client'

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Switch } from '@/components/ui/switch'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { 
  Calendar, 
  Clock, 
  Users, 
  Bell, 
  Plus, 
  ChefHat,
  ShoppingCart,
  AlertTriangle,
  CheckCircle,
  Settings,
  MessageSquare,
  Mail
} from 'lucide-react'
import { FamilyMealService } from '@/lib/family-meal-service'
import type { FamilyMeal, NotificationPreferences, TrackingPageData } from '@/lib/types'

interface TrackingPageProps {
  familyId: string
  userId: string
}

export default function TrackingPage({ familyId, userId }: TrackingPageProps) {
  const [data, setData] = useState<TrackingPageData | null>(null)
  const [loading, setLoading] = useState(false)
  const [showCreateMeal, setShowCreateMeal] = useState(false)
  const [showNotificationSettings, setShowNotificationSettings] = useState(false)
  const [preferences, setPreferences] = useState<NotificationPreferences | null>(null)

  useEffect(() => {
    loadData()
    loadPreferences()
  }, [familyId, userId])

  const loadData = async () => {
    try {
      setLoading(true)
      const [familyMeals, upcomingMeals] = await Promise.all([
        FamilyMealService.getFamilyMeals(familyId),
        FamilyMealService.getUpcomingMeals(familyId)
      ])

      const recentMeals = familyMeals
        .filter(meal => meal.status === 'completed')
        .sort((a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime())
        .slice(0, 5)

      setData({
        familyMeals,
        upcomingMeals,
        recentMeals,
        notificationStats: {
          totalSent: 0,
          appNotifications: 0,
          whatsappNotifications: 0,
          emailNotifications: 0
        }
      })
    } catch (error) {
      console.error('Failed to load tracking data:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadPreferences = async () => {
    try {
      const prefs = await FamilyMealService.getNotificationPreferences(userId)
      setPreferences(prefs)
    } catch (error) {
      console.error('Failed to load preferences:', error)
    }
  }

  const createFamilyMeal = async (mealData: {
    name: string
    description: string
    date: string
    time: string
    ingredients: Array<{ name: string; quantity: string; unit: string; category: string }>
  }) => {
    try {
      const meal = await FamilyMealService.createFamilyMeal(
        familyId,
        mealData.name,
        mealData.description,
        mealData.date,
        mealData.time,
        userId,
        mealData.ingredients
      )

      // Create notifications based on preferences
      if (preferences?.mealReminders) {
        const reminderTime = new Date(`${mealData.date}T${mealData.time}`)
        reminderTime.setMinutes(reminderTime.getMinutes() - (preferences.reminderTiming.meals || 30))

        if (preferences.appNotifications) {
          await FamilyMealService.createMealNotification(
            meal.id,
            'app',
            [userId],
            reminderTime.toISOString(),
            `Reminder: ${mealData.name} is scheduled for ${mealData.time}`
          )
        }

        if (preferences.whatsappNotifications && preferences.whatsappNumber) {
          await FamilyMealService.createMealNotification(
            meal.id,
            'whatsapp',
            [userId],
            reminderTime.toISOString(),
            `🍽️ Family Meal Reminder: ${mealData.name} at ${mealData.time}`
          )
        }

        if (preferences.emailNotifications && preferences.emailAddress) {
          await FamilyMealService.createMealNotification(
            meal.id,
            'email',
            [userId],
            reminderTime.toISOString(),
            `Family Meal Reminder: ${mealData.name}`
          )
        }
      }

      setShowCreateMeal(false)
      loadData()
    } catch (error) {
      console.error('Failed to create meal:', error)
    }
  }

  const updatePreferences = async (newPreferences: Partial<NotificationPreferences>) => {
    try {
      const updated = await FamilyMealService.updateNotificationPreferences(userId, newPreferences)
      setPreferences(updated)
    } catch (error) {
      console.error('Failed to update preferences:', error)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Family Tracking</h1>
          <p className="text-gray-600">Manage family meals and notifications</p>
        </div>
        <div className="flex gap-2">
          <Button onClick={() => setShowNotificationSettings(true)} variant="outline">
            <Settings className="w-4 h-4 mr-2" />
            Notifications
          </Button>
          <Button onClick={() => setShowCreateMeal(true)} className="bg-purple-600 hover:bg-purple-700">
            <Plus className="w-4 h-4 mr-2" />
            Create Meal
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <ChefHat className="w-8 h-8 text-purple-600" />
              <div>
                <p className="text-sm text-gray-600">Total Meals</p>
                <p className="text-2xl font-bold">{data?.familyMeals.length || 0}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <Calendar className="w-8 h-8 text-blue-600" />
              <div>
                <p className="text-sm text-gray-600">Upcoming</p>
                <p className="text-2xl font-bold">{data?.upcomingMeals.length || 0}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <Bell className="w-8 h-8 text-green-600" />
              <div>
                <p className="text-sm text-gray-600">Notifications</p>
                <p className="text-2xl font-bold">{data?.notificationStats.totalSent || 0}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <Users className="w-8 h-8 text-orange-600" />
              <div>
                <p className="text-sm text-gray-600">Participants</p>
                <p className="text-2xl font-bold">
                  {data?.familyMeals.reduce((sum, meal) => sum + meal.participants.length, 0) || 0}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Content */}
      <Tabs defaultValue="upcoming" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="upcoming">Upcoming Meals</TabsTrigger>
          <TabsTrigger value="recent">Recent Meals</TabsTrigger>
          <TabsTrigger value="all">All Meals</TabsTrigger>
        </TabsList>

        <TabsContent value="upcoming" className="space-y-4">
          {data?.upcomingMeals.length === 0 ? (
            <Card>
              <CardContent className="p-8 text-center">
                <Calendar className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">No Upcoming Meals</h3>
                <p className="text-gray-600 mb-4">Create your first family meal to get started</p>
                <Button onClick={() => setShowCreateMeal(true)} className="bg-purple-600 hover:bg-purple-700">
                  <Plus className="w-4 h-4 mr-2" />
                  Create Meal
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {data?.upcomingMeals.map((meal) => (
                <MealCard key={meal.id} meal={meal} onStatusUpdate={loadData} />
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="recent" className="space-y-4">
          {data?.recentMeals.length === 0 ? (
            <Card>
              <CardContent className="p-8 text-center">
                <CheckCircle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">No Recent Meals</h3>
                <p className="text-gray-600">Completed meals will appear here</p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {data?.recentMeals.map((meal) => (
                <MealCard key={meal.id} meal={meal} onStatusUpdate={loadData} />
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="all" className="space-y-4">
          <div className="space-y-4">
            {data?.familyMeals.map((meal) => (
              <MealCard key={meal.id} meal={meal} onStatusUpdate={loadData} />
            ))}
          </div>
        </TabsContent>
      </Tabs>

      {/* Create Meal Dialog */}
      {showCreateMeal && (
        <CreateMealDialog
          onClose={() => setShowCreateMeal(false)}
          onCreate={createFamilyMeal}
        />
      )}

      {/* Notification Settings Dialog */}
      {showNotificationSettings && preferences && (
        <NotificationSettingsDialog
          preferences={preferences}
          onClose={() => setShowNotificationSettings(false)}
          onSave={updatePreferences}
        />
      )}
    </div>
  )
}

// Meal Card Component
function MealCard({ meal, onStatusUpdate }: { meal: FamilyMeal; onStatusUpdate: () => void }) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'planned': return 'bg-blue-100 text-blue-800'
      case 'cooking': return 'bg-yellow-100 text-yellow-800'
      case 'completed': return 'bg-green-100 text-green-800'
      case 'cancelled': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const updateStatus = async (newStatus: FamilyMeal['status']) => {
    try {
      await FamilyMealService.updateMealStatus(meal.id, newStatus)
      onStatusUpdate()
    } catch (error) {
      console.error('Failed to update status:', error)
    }
  }

  return (
    <Card>
      <CardContent className="p-4">
        <div className="flex items-start justify-between mb-3">
          <div className="flex-1">
            <h3 className="font-semibold text-gray-900 mb-1">{meal.name}</h3>
            <p className="text-sm text-gray-600 mb-2">{meal.description}</p>
            <div className="flex items-center gap-4 text-sm text-gray-500">
              <div className="flex items-center gap-1">
                <Calendar className="w-4 h-4" />
                {meal.date}
              </div>
              <div className="flex items-center gap-1">
                <Clock className="w-4 h-4" />
                {meal.time}
              </div>
              <div className="flex items-center gap-1">
                <Users className="w-4 h-4" />
                {meal.participants.length} participants
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Badge className={getStatusColor(meal.status)}>
              {meal.status}
            </Badge>
            {meal.status === 'planned' && (
              <Button
                size="sm"
                onClick={() => updateStatus('cooking')}
                className="bg-yellow-600 hover:bg-yellow-700"
              >
                Start Cooking
              </Button>
            )}
            {meal.status === 'cooking' && (
              <Button
                size="sm"
                onClick={() => updateStatus('completed')}
                className="bg-green-600 hover:bg-green-700"
              >
                Complete
              </Button>
            )}
          </div>
        </div>

        {/* Ingredients */}
        <div className="space-y-2">
          <h4 className="text-sm font-medium text-gray-700">Ingredients:</h4>
          <div className="flex flex-wrap gap-2">
            {meal.ingredients.map((ingredient) => (
              <Badge
                key={ingredient.id}
                variant={ingredient.isAvailable ? "default" : "secondary"}
                className={ingredient.needsShopping ? "bg-red-100 text-red-800" : ""}
              >
                {ingredient.name} ({ingredient.quantity}{ingredient.unit})
              </Badge>
            ))}
          </div>
        </div>

        {/* Notifications */}
        {meal.notifications.length > 0 && (
          <div className="mt-3 pt-3 border-t">
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <Bell className="w-4 h-4" />
              {meal.notifications.length} notification{meal.notifications.length !== 1 ? 's' : ''} scheduled
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

// Create Meal Dialog Component
function CreateMealDialog({ onClose, onCreate }: { onClose: () => void; onCreate: (data: any) => void }) {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    date: '',
    time: '',
    ingredients: [{ name: '', quantity: '', unit: '', category: '' }]
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onCreate(formData)
  }

  const addIngredient = () => {
    setFormData(prev => ({
      ...prev,
      ingredients: [...prev.ingredients, { name: '', quantity: '', unit: '', category: '' }]
    }))
  }

  const removeIngredient = (index: number) => {
    setFormData(prev => ({
      ...prev,
      ingredients: prev.ingredients.filter((_, i) => i !== index)
    }))
  }

  const updateIngredient = (index: number, field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      ingredients: prev.ingredients.map((ing, i) => 
        i === index ? { ...ing, [field]: value } : ing
      )
    }))
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold">Create Family Meal</h2>
            <Button variant="ghost" onClick={onClose}>×</Button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="name">Meal Name</Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                  required
                />
              </div>
              <div>
                <Label htmlFor="date">Date</Label>
                <Input
                  id="date"
                  type="date"
                  value={formData.date}
                  onChange={(e) => setFormData(prev => ({ ...prev, date: e.target.value }))}
                  required
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="time">Time</Label>
                <Input
                  id="time"
                  type="time"
                  value={formData.time}
                  onChange={(e) => setFormData(prev => ({ ...prev, time: e.target.value }))}
                  required
                />
              </div>
            </div>

            <div>
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={formData.description}
                onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                rows={3}
              />
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <Label>Ingredients</Label>
                <Button type="button" onClick={addIngredient} size="sm" variant="outline">
                  <Plus className="w-4 h-4 mr-1" />
                  Add
                </Button>
              </div>
              <div className="space-y-2">
                {formData.ingredients.map((ingredient, index) => (
                  <div key={index} className="grid grid-cols-5 gap-2 items-center">
                    <Input
                      placeholder="Name"
                      value={ingredient.name}
                      onChange={(e) => updateIngredient(index, 'name', e.target.value)}
                    />
                    <Input
                      placeholder="Quantity"
                      value={ingredient.quantity}
                      onChange={(e) => updateIngredient(index, 'quantity', e.target.value)}
                    />
                    <Select
                      value={ingredient.unit}
                      onValueChange={(value) => updateIngredient(index, 'unit', value)}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Unit" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="g">g</SelectItem>
                        <SelectItem value="kg">kg</SelectItem>
                        <SelectItem value="ml">ml</SelectItem>
                        <SelectItem value="l">l</SelectItem>
                        <SelectItem value="pieces">pieces</SelectItem>
                        <SelectItem value="cups">cups</SelectItem>
                      </SelectContent>
                    </Select>
                    <Input
                      placeholder="Category"
                      value={ingredient.category}
                      onChange={(e) => updateIngredient(index, 'category', e.target.value)}
                    />
                    <Button
                      type="button"
                      onClick={() => removeIngredient(index)}
                      size="sm"
                      variant="outline"
                      className="text-red-600"
                    >
                      Remove
                    </Button>
                  </div>
                ))}
              </div>
            </div>

            <div className="flex gap-2 pt-4">
              <Button type="submit" className="flex-1 bg-purple-600 hover:bg-purple-700">
                Create Meal
              </Button>
              <Button type="button" onClick={onClose} variant="outline">
                Cancel
              </Button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}

// Notification Settings Dialog Component
function NotificationSettingsDialog({ 
  preferences, 
  onClose, 
  onSave 
}: { 
  preferences: NotificationPreferences; 
  onClose: () => void; 
  onSave: (prefs: Partial<NotificationPreferences>) => void;
}) {
  const [formData, setFormData] = useState(preferences)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSave(formData)
    onClose()
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold">Notification Settings</h2>
            <Button variant="ghost" onClick={onClose}>×</Button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Notification Types */}
            <div className="space-y-4">
              <h3 className="font-medium">Notification Types</h3>
              
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Bell className="w-4 h-4" />
                    <span>App Notifications</span>
                  </div>
                  <Switch
                    checked={formData.appNotifications}
                    onCheckedChange={(checked) => setFormData(prev => ({ ...prev, appNotifications: checked }))}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <MessageSquare className="w-4 h-4" />
                    <span>WhatsApp Notifications</span>
                  </div>
                  <Switch
                    checked={formData.whatsappNotifications}
                    onCheckedChange={(checked) => setFormData(prev => ({ ...prev, whatsappNotifications: checked }))}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Mail className="w-4 h-4" />
                    <span>Email Notifications</span>
                  </div>
                  <Switch
                    checked={formData.emailNotifications}
                    onCheckedChange={(checked) => setFormData(prev => ({ ...prev, emailNotifications: checked }))}
                  />
                </div>
              </div>
            </div>

            {/* Contact Information */}
            {(formData.whatsappNotifications || formData.emailNotifications) && (
              <div className="space-y-4">
                <h3 className="font-medium">Contact Information</h3>
                
                {formData.whatsappNotifications && (
                  <div>
                    <Label htmlFor="whatsapp">WhatsApp Number</Label>
                    <Input
                      id="whatsapp"
                      type="tel"
                      placeholder="+1234567890"
                      value={formData.whatsappNumber || ''}
                      onChange={(e) => setFormData(prev => ({ ...prev, whatsappNumber: e.target.value }))}
                    />
                  </div>
                )}

                {formData.emailNotifications && (
                  <div>
                    <Label htmlFor="email">Email Address</Label>
                    <Input
                      id="email"
                      type="email"
                      placeholder="user@example.com"
                      value={formData.emailAddress || ''}
                      onChange={(e) => setFormData(prev => ({ ...prev, emailAddress: e.target.value }))}
                    />
                  </div>
                )}
              </div>
            )}

            {/* Reminder Settings */}
            <div className="space-y-4">
              <h3 className="font-medium">Reminder Timing</h3>
              
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <Label htmlFor="mealReminder">Meal Reminders (minutes before)</Label>
                  <Input
                    id="mealReminder"
                    type="number"
                    value={formData.reminderTiming.meals}
                    onChange={(e) => setFormData(prev => ({ 
                      ...prev, 
                      reminderTiming: { ...prev.reminderTiming, meals: parseInt(e.target.value) || 30 }
                    }))}
                  />
                </div>
                
                <div>
                  <Label htmlFor="shoppingReminder">Shopping Reminders (hours before)</Label>
                  <Input
                    id="shoppingReminder"
                    type="number"
                    value={formData.reminderTiming.shopping}
                    onChange={(e) => setFormData(prev => ({ 
                      ...prev, 
                      reminderTiming: { ...prev.reminderTiming, shopping: parseInt(e.target.value) || 2 }
                    }))}
                  />
                </div>
                
                <div>
                  <Label htmlFor="expiryReminder">Expiry Alerts (days before)</Label>
                  <Input
                    id="expiryReminder"
                    type="number"
                    value={formData.reminderTiming.expiry}
                    onChange={(e) => setFormData(prev => ({ 
                      ...prev, 
                      reminderTiming: { ...prev.reminderTiming, expiry: parseInt(e.target.value) || 1 }
                    }))}
                  />
                </div>
              </div>
            </div>

            <div className="flex gap-2 pt-4">
              <Button type="submit" className="flex-1 bg-purple-600 hover:bg-purple-700">
                Save Settings
              </Button>
              <Button type="button" onClick={onClose} variant="outline">
                Cancel
              </Button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}
