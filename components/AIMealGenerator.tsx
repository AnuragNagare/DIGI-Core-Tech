'use client'

import React, { useState, useCallback } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { 
  X, 
  ChefHat, 
  Clock, 
  Users, 
  Heart,
  Sparkles,
  Utensils,
  Star,
  RefreshCw,
  Loader2
} from 'lucide-react'

interface InventoryItem {
  id: string
  name: string
  quantity: string
  unit: string
  category: string
  expiryDate?: string
  daysLeft?: number
}

interface MealSuggestion {
  id: string
  name: string
  description: string
  cookingTime: number
  servings: number
  difficulty: 'Easy' | 'Medium' | 'Hard'
  ingredients: string[]
  instructions: string[]
  nutritionalInfo?: {
    calories: number
    protein: number
    carbs: number
    fat: number
  }
}

interface AIMealGeneratorProps {
  onClose: () => void
  currentInventory: InventoryItem[]
}

export default function AIMealGenerator({ onClose, currentInventory }: AIMealGeneratorProps) {
  const [isGenerating, setIsGenerating] = useState(false)
  const [generatedMeals, setGeneratedMeals] = useState<MealSuggestion[]>([])
  const [preferences, setPreferences] = useState({
    dietType: 'any',
    cookingTime: 30,
    servings: 2,
    difficulty: 'any',
    cuisine: 'any'
  })

  const generateMeals = useCallback(async () => {
    setIsGenerating(true)
    
    try {
      const response = await fetch('http://localhost:8003/generate-meals', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: 'user123',
          available_ingredients: currentInventory.map(item => ({
            name: item.name,
            quantity: item.quantity,
            unit: item.unit,
            expires_in_days: item.daysLeft || 999
          })),
          // Waste optimization parameters
          prioritize_expiring: true,
          prioritize_high_quantity: true,
          expiring_ingredients: currentInventory
            .filter(item => (item.daysLeft || 999) <= 3)
            .map(item => ({
              name: item.name,
              expires_in_days: item.daysLeft || 0,
              quantity: item.quantity
            })),
          dietary_restrictions: preferences.dietType !== 'any' ? [preferences.dietType] : [],
          max_cooking_time: preferences.cookingTime,
          servings: preferences.servings,
          cuisine_preference: preferences.cuisine !== 'any' ? preferences.cuisine : undefined
        })
      })

      if (response.ok) {
        const data = await response.json()
        setGeneratedMeals(data.meals || [])
      } else {
        console.error('Failed to generate meals:', response.statusText)
        // Show fallback meals if API fails
        setGeneratedMeals(generateFallbackMeals())
      }
    } catch (error) {
      console.error('Error generating meals:', error)
      // Show fallback meals if API fails
      setGeneratedMeals(generateFallbackMeals())
    } finally {
      setIsGenerating(false)
    }
  }, [currentInventory, preferences])

  const generateFallbackMeals = useCallback((): MealSuggestion[] => {
    // Generate waste-optimized meals prioritizing expiring and high-quantity items
    const availableIngredients = currentInventory.map(item => item.name.toLowerCase())
    const fallbackMeals: MealSuggestion[] = []
    
    // Sort inventory by waste priority (expiring first, then high quantity)
    const wastePriorityItems = currentInventory
      .sort((a, b) => {
        // Priority 1: Expiring items (less days left = higher priority)
        if (a.daysLeft !== b.daysLeft) {
          return (a.daysLeft || 999) - (b.daysLeft || 999)
        }
        // Priority 2: High quantity items
        return parseFloat(b.quantity) - parseFloat(a.quantity)
      })
      .slice(0, 5) // Focus on top 5 priority items

    const expiringItems = currentInventory.filter(item => (item.daysLeft || 999) <= 3)
    const highQuantityItems = currentInventory.filter(item => parseFloat(item.quantity) >= 5)

    // Generate recipes prioritizing expiring bananas
    const bananaItem = currentInventory.find(item => item.name.toLowerCase().includes('banana'))
    if (availableIngredients.some(ing => ing.includes('banana')) && 
        bananaItem && bananaItem.daysLeft !== undefined && bananaItem.daysLeft <= 3) {
      fallbackMeals.push({
        id: '1',
        name: '🍌 Urgent Banana Rescue Pancakes',
        description: 'Quick rescue recipe for overripe bananas - prevents waste!',
        cookingTime: 15,
        servings: 2,
        difficulty: 'Easy',
        ingredients: ['2 ripe bananas (expiring)', '2 eggs', '1/4 cup milk', 'pinch of salt'],
        instructions: [
          'Use those overripe bananas before they spoil!',
          'Mash bananas thoroughly',
          'Beat in eggs and milk',
          'Cook on griddle until golden brown',
          'Serve hot - you just saved food from waste!'
        ],
        nutritionalInfo: {
          calories: 280,
          protein: 12,
          carbs: 35,
          fat: 8
        }
      })
    } else if (availableIngredients.some(ing => ing.includes('banana'))) {
      fallbackMeals.push({
        id: '1',
        name: 'Banana Pancakes',
        description: 'Quick and easy banana pancakes perfect for breakfast',
        cookingTime: 15,
        servings: 2,
        difficulty: 'Easy',
        ingredients: ['2 ripe bananas', '2 eggs', '1/4 cup milk', 'pinch of salt'],
        instructions: [
          'Mash bananas in a bowl',
          'Beat in eggs and milk',
          'Cook on griddle until golden brown',
          'Serve hot with syrup'
        ],
        nutritionalInfo: {
          calories: 280,
          protein: 12,
          carbs: 35,
          fat: 8
        }
      })
    }

    // Generate recipes prioritizing expiring milk or high-quantity milk
    const milkItem = currentInventory.find(item => item.name.toLowerCase().includes('milk'))
    if (availableIngredients.some(ing => ing.includes('milk'))) {
      const isExpiring = milkItem && (milkItem.daysLeft || 999) <= 3
      const isHighQuantity = milkItem && parseFloat(milkItem.quantity) >= 3
      
      fallbackMeals.push({
        id: '2',
        name: isExpiring ? '🥛 Urgent Milk Smoothie Bowl' : isHighQuantity ? '🥛 Bulk Milk Smoothie Bowl' : 'Creamy Smoothie Bowl',
        description: isExpiring ? 'Use milk before it expires - zero waste!' : 
                    isHighQuantity ? 'Great way to use up excess milk supply' : 
                    'Nutritious and refreshing smoothie bowl',
        cookingTime: 5,
        servings: isHighQuantity ? 3 : 1,
        difficulty: 'Easy',
        ingredients: isHighQuantity ? ['2 cups milk', 'seasonal fruits', 'honey to taste'] : 
                    ['1 cup milk', 'seasonal fruits', 'honey to taste'],
        instructions: isExpiring ? [
          'Use that milk before it spoils!',
          'Blend milk with fruits',
          'Pour into bowl',
          'Top with fresh fruits and nuts',
          'Enjoy guilt-free - no waste!'
        ] : [
          'Blend milk with fruits',
          'Pour into bowl', 
          'Top with fresh fruits and nuts',
          'Drizzle with honey'
        ],
        nutritionalInfo: {
          calories: isHighQuantity ? 480 : 320,
          protein: isHighQuantity ? 22 : 15,
          carbs: 45,
          fat: 10
        }
      })
    }

    // Generate recipes for expiring yogurt
    const yogurtItem = currentInventory.find(item => item.name.toLowerCase().includes('yogurt'))
    if (availableIngredients.some(ing => ing.includes('yogurt'))) {
      const isExpiring = yogurtItem && (yogurtItem.daysLeft || 999) <= 2
      
      fallbackMeals.push({
        id: '3',
        name: isExpiring ? '🥄 Rescue Yogurt Parfait' : 'Greek Yogurt Parfait',
        description: isExpiring ? 'Perfect rescue recipe for yogurt about to expire!' : 
                    'Healthy layered yogurt parfait with available ingredients',
        cookingTime: 5,
        servings: 1,
        difficulty: 'Easy',
        ingredients: ['Greek yogurt', 'fruits', 'granola or nuts'],
        instructions: isExpiring ? [
          'Quick! Use that yogurt before it expires',
          'Layer yogurt in a glass or bowl',
          'Add fruits and nuts',
          'Repeat layers',
          'Serve immediately - food saved!'
        ] : [
          'Layer yogurt in a glass or bowl',
          'Add fruits and nuts',
          'Repeat layers',
          'Serve immediately'
        ],
        nutritionalInfo: {
          calories: 250,
          protein: 20,
          carbs: 30,
          fat: 8
        }
      })
    }

    // If we have multiple expiring items, create a "Clean Out the Fridge" recipe
    if (expiringItems.length >= 3) {
      fallbackMeals.unshift({ // Add at the beginning for priority
        id: '0',
        name: '♻️ Clean Out the Fridge Special',
        description: `Rescue recipe using ${expiringItems.length} expiring ingredients - maximum waste prevention!`,
        cookingTime: 20,
        servings: 2,
        difficulty: 'Easy',
        ingredients: expiringItems.slice(0, 5).map(item => `${item.quantity} ${item.unit} ${item.name} (expiring in ${item.daysLeft}d)`),
        instructions: [
          'Perfect recipe to prevent food waste!',
          `Using: ${expiringItems.slice(0, 3).map(i => i.name).join(', ')}`,
          'Prepare all expiring ingredients first',
          'Combine creatively - stir fry, soup, or salad style',
          'Season well and cook until tender',
          'Congratulations - you just saved food from waste!'
        ],
        nutritionalInfo: {
          calories: 200,
          protein: 12,
          carbs: 25,
          fat: 8
        }
      })
    }

    // If no specific matches but we have high quantity items, create bulk recipe
    if (fallbackMeals.length === 0 && highQuantityItems.length > 0) {
      const highQuantityItem = highQuantityItems[0]
      fallbackMeals.push({
        id: '4',
        name: `📦 Bulk ${highQuantityItem.name} Special`,
        description: `Great way to use up your large quantity of ${highQuantityItem.name}!`,
        cookingTime: 25,
        servings: 4,
        difficulty: 'Easy',
                      ingredients: [`${Math.min(parseFloat(highQuantityItem.quantity), 4)} ${highQuantityItem.unit} ${highQuantityItem.name}`, 'basic ingredients'],
        instructions: [
          `Perfect for using up bulk ${highQuantityItem.name}`,
          'Prepare main ingredient generously',
          'Add complementary flavors',
          'Cook in larger portions for meal prep',
          'Store leftovers for later use'
        ],
        nutritionalInfo: {
          calories: 300,
          protein: 15,
          carbs: 35,
          fat: 12
        }
      })
    }

    // Default fallback if no priority items found
    if (fallbackMeals.length === 0) {
      fallbackMeals.push({
        id: '5',
        name: '🥗 Smart Inventory Salad',
        description: `Fresh and healthy mixed salad with your ${currentInventory.length} available ingredients`,
        cookingTime: 10,
        servings: 2,
        difficulty: 'Easy',
        ingredients: currentInventory.slice(0, 4).map(item => `${item.quantity} ${item.unit} ${item.name}`),
        instructions: [
          'Wash and prepare all available ingredients',
          'Mix creatively in a large bowl',
          'Add dressing of choice',
          'Use up what you have - smart cooking!'
        ],
        nutritionalInfo: {
          calories: 150,
          protein: 8,
          carbs: 20,
          fat: 6
        }
      })
    }

    return fallbackMeals
  }, [currentInventory])

  // Helper function to get waste reduction info
  const getWasteReductionInfo = () => {
    const expiringCount = currentInventory.filter(item => (item.daysLeft || 999) <= 3).length
    const highQuantityCount = currentInventory.filter(item => parseFloat(item.quantity) >= 5).length
    
    return {
      expiringCount,
      highQuantityCount,
      totalWastePrevention: expiringCount + highQuantityCount
    }
  }

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'Easy': return 'bg-green-100 text-green-800'
      case 'Medium': return 'bg-yellow-100 text-yellow-800'
      case 'Hard': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-4xl max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg flex items-center justify-center">
              <ChefHat className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-900">AI Meal Generator</h2>
              <p className="text-sm text-gray-500">Discover recipes from your ingredients</p>
            </div>
          </div>
          <Button variant="ghost" size="sm" onClick={onClose} className="rounded-full w-8 h-8 p-0">
            <X className="w-4 h-4" />
          </Button>
        </div>

        <div className="flex flex-1 min-h-0">
          {/* Sidebar - Preferences */}
          <div className="w-80 border-r border-gray-200 p-6 flex flex-col">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-purple-500" />
              Preferences
            </h3>

            <div className="space-y-4 flex-1">
              <div>
                <label className="text-sm font-medium text-gray-700 mb-2 block">
                  Diet Type
                </label>
                <select 
                  value={preferences.dietType}
                  onChange={(e) => setPreferences(prev => ({ ...prev, dietType: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                >
                  <option value="any">Any Diet</option>
                  <option value="vegetarian">Vegetarian</option>
                  <option value="vegan">Vegan</option>
                  <option value="gluten-free">Gluten-Free</option>
                  <option value="low-carb">Low Carb</option>
                </select>
              </div>

              <div>
                <label className="text-sm font-medium text-gray-700 mb-2 block">
                  Max Cooking Time: {preferences.cookingTime} min
                </label>
                <input
                  type="range"
                  min="5"
                  max="120"
                  value={preferences.cookingTime}
                  onChange={(e) => setPreferences(prev => ({ ...prev, cookingTime: parseInt(e.target.value) }))}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>5 min</span>
                  <span>2 hours</span>
                </div>
              </div>

              <div>
                <label className="text-sm font-medium text-gray-700 mb-2 block">
                  Servings: {preferences.servings}
                </label>
                <input
                  type="range"
                  min="1"
                  max="8"
                  value={preferences.servings}
                  onChange={(e) => setPreferences(prev => ({ ...prev, servings: parseInt(e.target.value) }))}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>1 person</span>
                  <span>8 people</span>
                </div>
              </div>

              <div>
                <label className="text-sm font-medium text-gray-700 mb-2 block">
                  Cuisine Style
                </label>
                <select 
                  value={preferences.cuisine}
                  onChange={(e) => setPreferences(prev => ({ ...prev, cuisine: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                >
                  <option value="any">Any Cuisine</option>
                  <option value="american">American</option>
                  <option value="italian">Italian</option>
                  <option value="asian">Asian</option>
                  <option value="mexican">Mexican</option>
                  <option value="mediterranean">Mediterranean</option>
                </select>
              </div>
            </div>

            <div className="mt-6 pt-4 border-t border-gray-200">
              {/* Waste Reduction Info */}
              {(() => {
                const wasteInfo = getWasteReductionInfo()
                return wasteInfo.totalWastePrevention > 0 && (
                  <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg">
                    <h4 className="text-sm font-medium text-green-800 mb-2 flex items-center gap-2">
                      ♻️ Waste Reduction Priority
                    </h4>
                    <div className="text-xs text-green-700 space-y-1">
                      {wasteInfo.expiringCount > 0 && (
                        <div>🕒 {wasteInfo.expiringCount} items expiring soon</div>
                      )}
                      {wasteInfo.highQuantityCount > 0 && (
                        <div>📦 {wasteInfo.highQuantityCount} high-quantity items</div>
                      )}
                      <div className="text-green-600 font-medium">
                        Recipes prioritized for zero waste!
                      </div>
                    </div>
                  </div>
                )
              })()}
              
              <div className="mb-3">
                <p className="text-sm font-medium text-gray-700 mb-2">Available Ingredients:</p>
                <p className="text-2xl font-bold text-purple-600">{currentInventory.length}</p>
              </div>
              <Button 
                onClick={generateMeals}
                disabled={isGenerating || currentInventory.length === 0}
                className="w-full bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 text-white h-11 rounded-lg font-medium"
              >
                {isGenerating ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    <ChefHat className="w-4 h-4 mr-2" />
                    Generate Meals
                  </>
                )}
              </Button>
            </div>
          </div>

          {/* Main Content - Generated Meals */}
          <div className="flex-1 flex flex-col">
            <div className="flex-1 overflow-y-auto">
              <div className="p-6">
                {generatedMeals.length === 0 ? (
                  <div className="flex flex-col items-center justify-center py-12 text-center">
                    <div className="w-20 h-20 bg-gray-100 rounded-2xl flex items-center justify-center mb-4">
                      <Utensils className="w-10 h-10 text-gray-400" />
                    </div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">Ready to Cook?</h3>
                    <p className="text-gray-500 mb-4 max-w-md">
                      Click "Generate Meals" to discover delicious recipes you can make with your current ingredients!
                    </p>
                    <Button 
                      onClick={generateMeals}
                      disabled={isGenerating || currentInventory.length === 0}
                      className="bg-purple-600 hover:bg-purple-700 text-white px-6"
                    >
                      {isGenerating ? (
                        <>
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          Generating...
                        </>
                      ) : (
                        <>
                          <ChefHat className="w-4 h-4 mr-2" />
                          Generate Meals
                        </>
                      )}
                    </Button>
                  </div>
                ) : (
                  <div className="space-y-6">
                    <div className="flex items-center justify-between">
                      <h3 className="text-xl font-bold text-gray-900">Suggested Meals</h3>
                      <Button 
                        onClick={generateMeals}
                        variant="outline"
                        size="sm"
                        disabled={isGenerating}
                        className="rounded-full"
                      >
                        <RefreshCw className="w-4 h-4 mr-2" />
                        Refresh
                      </Button>
                    </div>

                    <div className="grid gap-6">
                      {generatedMeals.map((meal) => (
                        <Card key={meal.id} className="hover:shadow-lg transition-all duration-200 border-l-4 border-l-purple-500">
                          <CardHeader className="pb-4">
                            <div className="flex items-start justify-between">
                              <div className="flex-1">
                                <CardTitle className="text-lg font-semibold text-gray-900 mb-2">
                                  {meal.name}
                                </CardTitle>
                                <CardDescription className="text-gray-600">
                                  {meal.description}
                                </CardDescription>
                              </div>
                              <Badge className={`ml-3 ${getDifficultyColor(meal.difficulty)}`}>
                                {meal.difficulty}
                              </Badge>
                            </div>

                            <div className="flex items-center gap-4 mt-3 text-sm text-gray-500">
                              <div className="flex items-center gap-1">
                                <Clock className="w-4 h-4" />
                                <span>{meal.cookingTime} min</span>
                              </div>
                              <div className="flex items-center gap-1">
                                <Users className="w-4 h-4" />
                                <span>{meal.servings} servings</span>
                              </div>
                              {meal.nutritionalInfo && (
                                <div className="flex items-center gap-1">
                                  <Heart className="w-4 h-4" />
                                  <span>{meal.nutritionalInfo.calories} cal</span>
                                </div>
                              )}
                            </div>
                          </CardHeader>

                          <CardContent className="pt-0">
                            <div className="grid md:grid-cols-2 gap-4">
                              <div>
                                <h4 className="font-medium text-gray-900 mb-2">Ingredients</h4>
                                <ul className="text-sm text-gray-600 space-y-1">
                                  {meal.ingredients.slice(0, 6).map((ingredient, idx) => (
                                    <li key={idx} className="flex items-center gap-2">
                                      <div className="w-1 h-1 bg-purple-500 rounded-full"></div>
                                      {ingredient}
                                    </li>
                                  ))}
                                  {meal.ingredients.length > 6 && (
                                    <li className="text-purple-600 text-xs">
                                      +{meal.ingredients.length - 6} more ingredients
                                    </li>
                                  )}
                                </ul>
                              </div>

                              <div>
                                <h4 className="font-medium text-gray-900 mb-2">Instructions</h4>
                                <ol className="text-sm text-gray-600 space-y-1">
                                  {meal.instructions.slice(0, 4).map((step, idx) => (
                                    <li key={idx} className="flex gap-2">
                                      <span className="text-purple-500 font-medium">{idx + 1}.</span>
                                      {step}
                                    </li>
                                  ))}
                                  {meal.instructions.length > 4 && (
                                    <li className="text-purple-600 text-xs ml-4">
                                      +{meal.instructions.length - 4} more steps
                                    </li>
                                  )}
                                </ol>
                              </div>
                            </div>

                            {meal.nutritionalInfo && (
                              <>
                                <Separator className="my-4" />
                                <div className="grid grid-cols-4 gap-4 text-center">
                                  <div>
                                    <div className="text-lg font-bold text-gray-900">{meal.nutritionalInfo.calories}</div>
                                    <div className="text-xs text-gray-500">Calories</div>
                                  </div>
                                  <div>
                                    <div className="text-lg font-bold text-gray-900">{meal.nutritionalInfo.protein}g</div>
                                    <div className="text-xs text-gray-500">Protein</div>
                                  </div>
                                  <div>
                                    <div className="text-lg font-bold text-gray-900">{meal.nutritionalInfo.carbs}g</div>
                                    <div className="text-xs text-gray-500">Carbs</div>
                                  </div>
                                  <div>
                                    <div className="text-lg font-bold text-gray-900">{meal.nutritionalInfo.fat}g</div>
                                    <div className="text-xs text-gray-500">Fat</div>
                                  </div>
                                </div>
                              </>
                            )}
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}