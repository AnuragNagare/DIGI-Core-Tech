import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Progress } from '@/components/ui/progress'
import { 
  ShoppingCart, 
  Brain, 
  TrendingUp, 
  Calendar,
  DollarSign,
  ThumbsUp,
  ThumbsDown,
  Sparkles,
  Target,
  Clock,
  BarChart3
} from 'lucide-react'

// Types
interface AIShoppingItem {
  name: string
  category: string
  brand?: string
  price?: number
  quantity: number
  unit: string
  priority_score: number
  confidence: number
  reason: string
}

interface ShoppingInsights {
  prediction_confidence: number
  categories_predicted: number
  seasonal_items: number
  frequent_items: number
  smart_suggestions: string
}

interface UserPatterns {
  top_categories: string[]
  shopping_frequency: number
  predicted_budget: number
}

interface AIShoppingListProps {
  currentInventory: any[]
  shoppingHistory: any[]
  userId: string
  onUpdateShoppingList: (items: any[]) => void
}

const AIShoppingList: React.FC<AIShoppingListProps> = ({ 
  currentInventory, 
  shoppingHistory, 
  userId, 
  onUpdateShoppingList 
}) => {
  const [aiPredictions, setAiPredictions] = useState<AIShoppingItem[]>([])
  const [insights, setInsights] = useState<ShoppingInsights | null>(null)
  const [userPatterns, setUserPatterns] = useState<UserPatterns | null>(null)
  const [loading, setLoading] = useState(false)
  const [budgetLimit, setBudgetLimit] = useState<number>(100)
  const [selectedItems, setSelectedItems] = useState<Set<string>>(new Set())
  const [userFeedback, setUserFeedback] = useState<Record<string, string>>({})

  // Generate AI Shopping List
  const generateAIShoppingList = async () => {
    setLoading(true)
    try {
      const response = await fetch('/api/shopping/ai-predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          current_inventory: currentInventory,
          shopping_history: shoppingHistory,
          budget_limit: budgetLimit
        })
      })

      if (response.ok) {
        const data = await response.json()
        if (data.success) {
          setAiPredictions(data.shopping_list || [])
          setInsights(data.insights || null)
          setUserPatterns(data.user_patterns || null)
        }
      }
    } catch (error) {
      console.error('Failed to generate AI shopping list:', error)
    } finally {
      setLoading(false)
    }
  }

  // Submit feedback for learning
  const submitFeedback = async (itemName: string, feedback: string) => {
    try {
      await fetch('/api/shopping/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          item_name: itemName,
          feedback: feedback
        })
      })

      setUserFeedback(prev => ({ ...prev, [itemName]: feedback }))
    } catch (error) {
      console.error('Failed to submit feedback:', error)
    }
  }

  // Toggle item selection
  const toggleItemSelection = (itemName: string) => {
    const newSelection = new Set(selectedItems)
    if (newSelection.has(itemName)) {
      newSelection.delete(itemName)
    } else {
      newSelection.add(itemName)
    }
    setSelectedItems(newSelection)
  }

  // Add selected items to shopping list
  const addToShoppingList = () => {
    const selectedPredictions = aiPredictions.filter(item => 
      selectedItems.has(item.name)
    )
    
    const shoppingListItems = selectedPredictions.map(item => ({
      id: Date.now() + Math.random(),
      name: item.name,
      quantity: item.quantity,
      unit: item.unit,
      category: item.category,
      completed: false,
      aiGenerated: true,
      confidence: item.confidence,
      reason: item.reason
    }))

    onUpdateShoppingList(shoppingListItems)
    setSelectedItems(new Set())
  }

  // Get priority color
  const getPriorityColor = (score: number) => {
    if (score >= 0.8) return 'bg-red-100 text-red-800 border-red-200'
    if (score >= 0.6) return 'bg-orange-100 text-orange-800 border-orange-200'
    if (score >= 0.4) return 'bg-yellow-100 text-yellow-800 border-yellow-200'
    return 'bg-gray-100 text-gray-800 border-gray-200'
  }

  // Get priority label
  const getPriorityLabel = (score: number) => {
    if (score >= 0.8) return 'High Priority'
    if (score >= 0.6) return 'Medium Priority'
    if (score >= 0.4) return 'Low Priority'
    return 'Optional'
  }

  // Get confidence color
  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-600'
    if (confidence >= 0.6) return 'text-yellow-600'
    return 'text-gray-600'
  }

  useEffect(() => {
    if (currentInventory.length > 0 && shoppingHistory.length > 0) {
      generateAIShoppingList()
    }
  }, [currentInventory, shoppingHistory, userId])

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Brain className="w-5 h-5 text-purple-600" />
            <CardTitle>🤖 AI Shopping List Generator</CardTitle>
          </div>
          <CardDescription>
            Intelligent shopping predictions based on your patterns and preferences
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-4 mb-4">
            <div className="flex items-center gap-2">
              <DollarSign className="w-4 h-4" />
              <span className="text-sm">Budget Limit:</span>
              <Input
                type="number"
                value={budgetLimit}
                onChange={(e) => setBudgetLimit(Number(e.target.value))}
                className="w-20"
                min="0"
              />
            </div>
            <Button 
              onClick={generateAIShoppingList} 
              disabled={loading}
              className="bg-purple-600 hover:bg-purple-700"
            >
              {loading ? 'Generating...' : '✨ Generate Smart List'}
            </Button>
          </div>

          {/* Quick Stats */}
          {insights && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
              <div className="text-center p-3 bg-purple-50 rounded-lg">
                <div className="text-2xl font-bold text-purple-600">
                  {Math.round(insights.prediction_confidence * 100)}%
                </div>
                <div className="text-xs text-purple-700">Confidence</div>
              </div>
              <div className="text-center p-3 bg-blue-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">
                  {insights.categories_predicted}
                </div>
                <div className="text-xs text-blue-700">Categories</div>
              </div>
              <div className="text-center p-3 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">
                  {insights.frequent_items}
                </div>
                <div className="text-xs text-green-700">Frequent</div>
              </div>
              <div className="text-center p-3 bg-orange-50 rounded-lg">
                <div className="text-2xl font-bold text-orange-600">
                  {insights.seasonal_items}
                </div>
                <div className="text-xs text-orange-700">Seasonal</div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Main Content */}
      <Tabs defaultValue="predictions" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="predictions">
            <Target className="w-4 h-4 mr-2" />
            Smart Predictions
          </TabsTrigger>
          <TabsTrigger value="insights">
            <BarChart3 className="w-4 h-4 mr-2" />
            Shopping Insights
          </TabsTrigger>
          <TabsTrigger value="patterns">
            <TrendingUp className="w-4 h-4 mr-2" />
            Your Patterns
          </TabsTrigger>
        </TabsList>

        {/* Predictions Tab */}
        <TabsContent value="predictions">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Sparkles className="w-5 h-5" />
                AI Predictions ({aiPredictions.length} items)
              </CardTitle>
              {selectedItems.size > 0 && (
                <Button onClick={addToShoppingList} className="ml-auto">
                  Add {selectedItems.size} Items to List
                </Button>
              )}
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {aiPredictions.map((item, index) => (
                  <div
                    key={index}
                    className={`p-4 border rounded-lg transition-all ${
                      selectedItems.has(item.name) 
                        ? 'border-purple-500 bg-purple-50' 
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3">
                          <input
                            type="checkbox"
                            checked={selectedItems.has(item.name)}
                            onChange={() => toggleItemSelection(item.name)}
                            className="w-4 h-4 text-purple-600"
                          />
                          <div>
                            <h3 className="font-medium">{item.name}</h3>
                            <div className="flex items-center gap-2 mt-1">
                              <Badge variant="secondary" className="text-xs">
                                {item.category}
                              </Badge>
                              <Badge 
                                className={`text-xs ${getPriorityColor(item.priority_score)}`}
                              >
                                {getPriorityLabel(item.priority_score)}
                              </Badge>
                              <span className={`text-xs ${getConfidenceColor(item.confidence)}`}>
                                {Math.round(item.confidence * 100)}% confident
                              </span>
                            </div>
                          </div>
                        </div>

                        <div className="mt-2 flex items-center justify-between">
                          <div className="text-sm text-gray-600">
                            {item.quantity} {item.unit} • {item.reason}
                            {item.price && <span> • ${item.price.toFixed(2)}</span>}
                          </div>

                          {/* Feedback Buttons */}
                          <div className="flex items-center gap-1">
                            <button
                              onClick={() => submitFeedback(item.name, 'positive')}
                              className={`p-1 rounded hover:bg-green-100 ${
                                userFeedback[item.name] === 'positive' ? 'bg-green-100' : ''
                              }`}
                            >
                              <ThumbsUp className="w-3 h-3 text-green-600" />
                            </button>
                            <button
                              onClick={() => submitFeedback(item.name, 'negative')}
                              className={`p-1 rounded hover:bg-red-100 ${
                                userFeedback[item.name] === 'negative' ? 'bg-red-100' : ''
                              }`}
                            >
                              <ThumbsDown className="w-3 h-3 text-red-600" />
                            </button>
                          </div>
                        </div>

                        {/* Priority Progress Bar */}
                        <div className="mt-2">
                          <div className="flex items-center gap-2">
                            <span className="text-xs text-gray-500">Priority:</span>
                            <Progress 
                              value={item.priority_score * 100} 
                              className="flex-1 h-2"
                            />
                            <span className="text-xs text-gray-500">
                              {Math.round(item.priority_score * 100)}%
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}

                {aiPredictions.length === 0 && !loading && (
                  <div className="text-center py-8 text-gray-500">
                    <Brain className="w-12 h-12 mx-auto mb-3 opacity-50" />
                    <p>No predictions available. Try generating your AI shopping list!</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Insights Tab */}
        <TabsContent value="insights">
          <Card>
            <CardHeader>
              <CardTitle>Shopping Insights</CardTitle>
            </CardHeader>
            <CardContent>
              {insights ? (
                <div className="space-y-4">
                  <div className="p-4 bg-blue-50 rounded-lg">
                    <h3 className="font-medium text-blue-900 mb-2">
                      Smart Analysis
                    </h3>
                    <p className="text-blue-800 text-sm">
                      {insights.smart_suggestions}
                    </p>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="p-4 border rounded-lg">
                      <h4 className="font-medium mb-2">Prediction Quality</h4>
                      <Progress 
                        value={insights.prediction_confidence * 100} 
                        className="mb-2"
                      />
                      <p className="text-sm text-gray-600">
                        {Math.round(insights.prediction_confidence * 100)}% average confidence
                      </p>
                    </div>

                    <div className="p-4 border rounded-lg">
                      <h4 className="font-medium mb-2">Categories Covered</h4>
                      <div className="text-2xl font-bold text-purple-600 mb-1">
                        {insights.categories_predicted}
                      </div>
                      <p className="text-sm text-gray-600">
                        Different product categories
                      </p>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <BarChart3 className="w-12 h-12 mx-auto mb-3 opacity-50" />
                  <p>Generate your AI shopping list to see insights!</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Patterns Tab */}
        <TabsContent value="patterns">
          <Card>
            <CardHeader>
              <CardTitle>Your Shopping Patterns</CardTitle>
            </CardHeader>
            <CardContent>
              {userPatterns ? (
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="p-4 border rounded-lg">
                      <h4 className="font-medium mb-2">Shopping Activity</h4>
                      <div className="text-2xl font-bold text-green-600 mb-1">
                        {userPatterns.shopping_frequency}
                      </div>
                      <p className="text-sm text-gray-600">Shopping sessions</p>
                    </div>

                    <div className="p-4 border rounded-lg">
                      <h4 className="font-medium mb-2">Predicted Budget</h4>
                      <div className="text-2xl font-bold text-blue-600 mb-1">
                        ${userPatterns.predicted_budget.toFixed(2)}
                      </div>
                      <p className="text-sm text-gray-600">For this list</p>
                    </div>

                    <div className="p-4 border rounded-lg">
                      <h4 className="font-medium mb-2">Top Categories</h4>
                      <div className="space-y-1">
                        {userPatterns.top_categories.slice(0, 3).map((category, idx) => (
                          <Badge key={idx} variant="outline" className="text-xs mr-1">
                            {category}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <TrendingUp className="w-12 h-12 mx-auto mb-3 opacity-50" />
                  <p>Build shopping history to see your patterns!</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

export default AIShoppingList