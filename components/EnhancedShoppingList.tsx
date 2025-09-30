import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Checkbox } from '@/components/ui/checkbox'
import AIShoppingList from './AIShoppingList'
import SmartSuggestions from './SmartSuggestions'
import ShoppingAnalytics from './ShoppingAnalytics'
import {
  ShoppingBag,
  Plus,
  Brain,
  TrendingUp,
  BarChart3,
  List,
  Trash2,
  Edit,
  Check,
  X
} from 'lucide-react'

interface ShoppingItem {
  id: string
  name: string
  quantity: number
  category?: string
  price?: number
  priority: 'low' | 'medium' | 'high'
  completed: boolean
  addedBy: 'user' | 'ai'
  confidence?: number
}

interface ShoppingListProps {
  userId: string
}

const EnhancedShoppingList: React.FC<ShoppingListProps> = ({ userId }) => {
  const [shoppingList, setShoppingList] = useState<ShoppingItem[]>([])
  const [newItemName, setNewItemName] = useState('')
  const [activeTab, setActiveTab] = useState('list')
  const [budget, setBudget] = useState(150)
  const [totalSpent, setTotalSpent] = useState(0)
  const [loading, setLoading] = useState(false)
  const [analyticsTimeRange, setAnalyticsTimeRange] = useState<'week' | 'month' | 'quarter' | 'year'>('month')

  // Add new item manually
  const addItem = (name: string, quantity: number = 1) => {
    if (!name.trim()) return

    const newItem: ShoppingItem = {
      id: Date.now().toString(),
      name: name.trim(),
      quantity,
      priority: 'medium',
      completed: false,
      addedBy: 'user'
    }

    setShoppingList(prev => [...prev, newItem])
    setNewItemName('')
  }

  // Add AI suggested items
  const addAISuggestions = (items: string[], confidence?: number) => {
    const newItems: ShoppingItem[] = items.map(item => ({
      id: `ai-${Date.now()}-${Math.random()}`,
      name: item,
      quantity: 1,
      priority: confidence && confidence > 0.8 ? 'high' : 'medium',
      completed: false,
      addedBy: 'ai',
      confidence
    }))

    setShoppingList(prev => [...prev, ...newItems])
  }

  // Toggle item completion
  const toggleItem = (id: string) => {
    setShoppingList(prev => 
      prev.map(item => 
        item.id === id ? { ...item, completed: !item.completed } : item
      )
    )
  }

  // Remove item
  const removeItem = (id: string) => {
    setShoppingList(prev => prev.filter(item => item.id !== id))
  }

  // Update item priority
  const updatePriority = (id: string, priority: 'low' | 'medium' | 'high') => {
    setShoppingList(prev => 
      prev.map(item => 
        item.id === id ? { ...item, priority } : item
      )
    )
  }

  // Update item quantity
  const updateQuantity = (id: string, quantity: number) => {
    if (quantity <= 0) return
    setShoppingList(prev => 
      prev.map(item => 
        item.id === id ? { ...item, quantity } : item
      )
    )
  }

  // Get priority color
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-red-100 text-red-800'
      case 'medium': return 'bg-yellow-100 text-yellow-800'
      case 'low': return 'bg-green-100 text-green-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  // Calculate statistics
  const completedItems = shoppingList.filter(item => item.completed).length
  const totalItems = shoppingList.length
  const aiSuggestedItems = shoppingList.filter(item => item.addedBy === 'ai').length
  const highPriorityItems = shoppingList.filter(item => item.priority === 'high' && !item.completed).length

  // Get recent purchases for analytics
  const getRecentPurchases = () => {
    // Mock data - in real app, this would come from purchase history
    return [
      {
        id: '1',
        date: new Date().toISOString(),
        items: shoppingList.filter(item => item.completed)
      }
    ]
  }

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      {/* Header */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <ShoppingBag className="w-6 h-6 text-blue-600" />
                🛒 AI-Powered Shopping List
              </CardTitle>
              <CardDescription>
                Smart shopping with AI predictions, analytics, and personalized suggestions
              </CardDescription>
            </div>
            
            <div className="flex items-center gap-4">
              <div className="text-right">
                <p className="text-sm text-gray-600">Budget Progress</p>
                <p className="text-lg font-bold">
                  ${totalSpent.toFixed(2)} / ${budget.toFixed(2)}
                </p>
              </div>
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Quick Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-blue-600">{totalItems}</div>
            <div className="text-sm text-gray-600">Total Items</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-green-600">{completedItems}</div>
            <div className="text-sm text-gray-600">Completed</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-purple-600">{aiSuggestedItems}</div>
            <div className="text-sm text-gray-600">AI Suggested</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-red-600">{highPriorityItems}</div>
            <div className="text-sm text-gray-600">High Priority</div>
          </CardContent>
        </Card>
      </div>

      {/* Main Content */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="list" className="flex items-center gap-2">
            <List className="w-4 h-4" />
            Shopping List
          </TabsTrigger>
          <TabsTrigger value="ai" className="flex items-center gap-2">
            <Brain className="w-4 h-4" />
            AI Predictions
          </TabsTrigger>
          <TabsTrigger value="suggestions" className="flex items-center gap-2">
            <TrendingUp className="w-4 h-4" />
            Smart Suggestions
          </TabsTrigger>
          <TabsTrigger value="analytics" className="flex items-center gap-2">
            <BarChart3 className="w-4 h-4" />
            Analytics
          </TabsTrigger>
        </TabsList>

        {/* Shopping List Tab */}
        <TabsContent value="list" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Current Shopping List</CardTitle>
              <CardDescription>
                Add items manually or let AI suggest what you need
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Add Item Form */}
              <div className="flex gap-2">
                <Input
                  placeholder="Add new item..."
                  value={newItemName}
                  onChange={(e) => setNewItemName(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && addItem(newItemName)}
                  className="flex-1"
                />
                <Button 
                  onClick={() => addItem(newItemName)}
                  disabled={!newItemName.trim()}
                >
                  <Plus className="w-4 h-4" />
                  Add
                </Button>
              </div>

              {/* Shopping Items */}
              <div className="space-y-2">
                {shoppingList.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    <ShoppingBag className="w-12 h-12 mx-auto mb-3 opacity-50" />
                    <p>Your shopping list is empty</p>
                    <p className="text-sm">Add items manually or check AI predictions</p>
                  </div>
                ) : (
                  shoppingList.map((item) => (
                    <Card key={item.id} className={item.completed ? 'opacity-60' : ''}>
                      <CardContent className="p-3">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            <Checkbox
                              checked={item.completed}
                              onCheckedChange={() => toggleItem(item.id)}
                            />
                            
                            <div className="flex-1">
                              <div className="flex items-center gap-2">
                                <span className={item.completed ? 'line-through' : ''}>
                                  {item.name}
                                </span>
                                {item.addedBy === 'ai' && (
                                  <Badge variant="secondary" className="text-xs">
                                    AI
                                  </Badge>
                                )}
                                {item.confidence && (
                                  <Badge variant="outline" className="text-xs">
                                    {Math.round(item.confidence * 100)}%
                                  </Badge>
                                )}
                              </div>
                              <div className="flex items-center gap-2 mt-1">
                                <Badge 
                                  variant="secondary" 
                                  className={`text-xs ${getPriorityColor(item.priority)}`}
                                >
                                  {item.priority}
                                </Badge>
                                <span className="text-xs text-gray-500">
                                  Qty: {item.quantity}
                                </span>
                              </div>
                            </div>
                          </div>

                          <div className="flex items-center gap-2">
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => updateQuantity(item.id, item.quantity - 1)}
                              disabled={item.quantity <= 1}
                            >
                              -
                            </Button>
                            <span className="w-8 text-center">{item.quantity}</span>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => updateQuantity(item.id, item.quantity + 1)}
                            >
                              +
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => removeItem(item.id)}
                            >
                              <Trash2 className="w-3 h-3" />
                            </Button>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* AI Predictions Tab */}
        <TabsContent value="ai" className="space-y-4">
          <AIShoppingList
            userId={userId}
            currentItems={shoppingList.map(item => item.name)}
            onAddItems={addAISuggestions}
          />
        </TabsContent>

        {/* Smart Suggestions Tab */}
        <TabsContent value="suggestions" className="space-y-4">
          <SmartSuggestions
            userId={userId}
            currentMonth={new Date().toLocaleString('default', { month: 'long' })}
            budget={budget}
            recentPurchases={getRecentPurchases()}
            onAddSuggestion={addAISuggestions}
          />
        </TabsContent>

        {/* Analytics Tab */}
        <TabsContent value="analytics" className="space-y-4">
          <ShoppingAnalytics
            userId={userId}
            timeRange={analyticsTimeRange}
            onTimeRangeChange={setAnalyticsTimeRange}
          />
        </TabsContent>
      </Tabs>
    </div>
  )
}

export default EnhancedShoppingList