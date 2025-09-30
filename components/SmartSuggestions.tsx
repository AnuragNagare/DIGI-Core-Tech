import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  Lightbulb, 
  Calendar,
  TrendingUp,
  ShoppingBag,
  Clock,
  DollarSign,
  Zap,
  Target
} from 'lucide-react'

interface SmartSuggestion {
  type: 'seasonal' | 'trending' | 'budget' | 'frequent' | 'urgent'
  title: string
  description: string
  items: string[]
  confidence: number
  savings?: number
  urgency?: 'low' | 'medium' | 'high'
}

interface SmartSuggestionsProps {
  userId: string
  currentMonth: string
  budget: number
  recentPurchases: any[]
  onAddSuggestion: (items: string[]) => void
}

const SmartSuggestions: React.FC<SmartSuggestionsProps> = ({
  userId,
  currentMonth,
  budget,
  recentPurchases,
  onAddSuggestion
}) => {
  const [suggestions, setSuggestions] = useState<SmartSuggestion[]>([])
  const [loading, setLoading] = useState(false)

  // Generate smart suggestions
  const generateSmartSuggestions = async () => {
    setLoading(true)
    try {
      // Seasonal suggestions
      const seasonalResponse = await fetch(`/api/shopping/seasonal/${currentMonth}`)
      const seasonalData = await seasonalResponse.json()

      const smartSuggestions: SmartSuggestion[] = []

      // Add seasonal suggestions
      if (seasonalData.success && seasonalData.seasonal_recommendations.length > 0) {
        smartSuggestions.push({
          type: 'seasonal',
          title: `🌸 ${currentMonth} Seasonal Picks`,
          description: `Popular items for ${currentMonth} based on seasonal trends`,
          items: seasonalData.seasonal_recommendations,
          confidence: 0.8,
          urgency: 'medium'
        })
      }

      // Budget-friendly suggestions
      smartSuggestions.push({
        type: 'budget',
        title: '💰 Budget Smart Choices',
        description: 'Cost-effective items that offer great value',
        items: ['Generic brand cereals', 'Seasonal fruits', 'Bulk rice'],
        confidence: 0.7,
        savings: 15.50,
        urgency: 'low'
      })

      // Trending suggestions
      smartSuggestions.push({
        type: 'trending',
        title: '📈 Trending Now',
        description: 'Popular items other users are buying',
        items: ['Plant-based milk', 'Air fryer snacks', 'Kombucha'],
        confidence: 0.6,
        urgency: 'low'
      })

      // Frequent replenishment
      if (recentPurchases.length > 0) {
        const frequentItems = getFrequentItems(recentPurchases)
        if (frequentItems.length > 0) {
          smartSuggestions.push({
            type: 'frequent',
            title: '🔄 Ready for Refill',
            description: 'Items you buy regularly that might need restocking',
            items: frequentItems,
            confidence: 0.9,
            urgency: 'high'
          })
        }
      }

      setSuggestions(smartSuggestions)
    } catch (error) {
      console.error('Failed to generate smart suggestions:', error)
    } finally {
      setLoading(false)
    }
  }

  // Get frequent items from purchase history
  const getFrequentItems = (purchases: any[]) => {
    const itemCounts: Record<string, number> = {}
    
    purchases.forEach(purchase => {
      purchase.items?.forEach((item: any) => {
        itemCounts[item.name] = (itemCounts[item.name] || 0) + 1
      })
    })

    return Object.entries(itemCounts)
      .filter(([_, count]) => count >= 2)
      .sort(([_, a], [__, b]) => b - a)
      .slice(0, 3)
      .map(([name, _]) => name)
  }

  // Get suggestion icon
  const getSuggestionIcon = (type: string) => {
    switch (type) {
      case 'seasonal': return <Calendar className="w-4 h-4" />
      case 'trending': return <TrendingUp className="w-4 h-4" />
      case 'budget': return <DollarSign className="w-4 h-4" />
      case 'frequent': return <Clock className="w-4 h-4" />
      case 'urgent': return <Zap className="w-4 h-4" />
      default: return <Lightbulb className="w-4 h-4" />
    }
  }

  // Get suggestion color
  const getSuggestionColor = (type: string) => {
    switch (type) {
      case 'seasonal': return 'border-green-200 bg-green-50'
      case 'trending': return 'border-blue-200 bg-blue-50'
      case 'budget': return 'border-yellow-200 bg-yellow-50'
      case 'frequent': return 'border-purple-200 bg-purple-50'
      case 'urgent': return 'border-red-200 bg-red-50'
      default: return 'border-gray-200 bg-gray-50'
    }
  }

  // Get urgency badge color
  const getUrgencyColor = (urgency?: string) => {
    switch (urgency) {
      case 'high': return 'bg-red-100 text-red-800'
      case 'medium': return 'bg-yellow-100 text-yellow-800'
      case 'low': return 'bg-green-100 text-green-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  useEffect(() => {
    generateSmartSuggestions()
  }, [currentMonth, recentPurchases])

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Lightbulb className="w-5 h-5 text-yellow-600" />
              <CardTitle>💡 Smart Shopping Suggestions</CardTitle>
            </div>
            <Button 
              onClick={generateSmartSuggestions}
              disabled={loading}
              size="sm"
              variant="outline"
            >
              {loading ? 'Updating...' : 'Refresh'}
            </Button>
          </div>
          <CardDescription>
            AI-powered suggestions based on trends, seasons, and your shopping patterns
          </CardDescription>
        </CardHeader>
      </Card>

      <Tabs defaultValue="all" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="all">All</TabsTrigger>
          <TabsTrigger value="seasonal">Seasonal</TabsTrigger>
          <TabsTrigger value="budget">Budget</TabsTrigger>
          <TabsTrigger value="trending">Trending</TabsTrigger>
        </TabsList>

        <TabsContent value="all" className="space-y-3">
          {suggestions.map((suggestion, index) => (
            <Card 
              key={index} 
              className={`transition-all hover:shadow-md ${getSuggestionColor(suggestion.type)}`}
            >
              <CardContent className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      {getSuggestionIcon(suggestion.type)}
                      <h3 className="font-medium">{suggestion.title}</h3>
                      <Badge 
                        variant="secondary" 
                        className={getUrgencyColor(suggestion.urgency)}
                      >
                        {suggestion.urgency || 'info'}
                      </Badge>
                      <Badge variant="outline" className="text-xs">
                        {Math.round(suggestion.confidence * 100)}% confident
                      </Badge>
                    </div>

                    <p className="text-sm text-gray-600 mb-3">
                      {suggestion.description}
                    </p>

                    <div className="flex flex-wrap gap-1 mb-3">
                      {suggestion.items.map((item, itemIndex) => (
                        <Badge key={itemIndex} variant="secondary" className="text-xs">
                          {item}
                        </Badge>
                      ))}
                    </div>

                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4 text-sm text-gray-500">
                        {suggestion.savings && (
                          <span className="flex items-center gap-1">
                            <DollarSign className="w-3 h-3" />
                            Save ${suggestion.savings.toFixed(2)}
                          </span>
                        )}
                        <span className="flex items-center gap-1">
                          <Target className="w-3 h-3" />
                          {suggestion.items.length} items
                        </span>
                      </div>

                      <Button 
                        size="sm" 
                        onClick={() => onAddSuggestion(suggestion.items)}
                      >
                        Add to List
                      </Button>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}

          {suggestions.length === 0 && !loading && (
            <Card>
              <CardContent className="p-8 text-center">
                <Lightbulb className="w-12 h-12 mx-auto mb-3 opacity-50" />
                <p className="text-gray-500">No suggestions available right now.</p>
                <Button 
                  onClick={generateSmartSuggestions}
                  className="mt-3"
                  size="sm"
                >
                  Generate Suggestions
                </Button>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="seasonal" className="space-y-3">
          {suggestions
            .filter(s => s.type === 'seasonal')
            .map((suggestion, index) => (
              <Card key={index} className={getSuggestionColor(suggestion.type)}>
                <CardContent className="p-4">
                  <div className="flex items-center gap-2 mb-2">
                    {getSuggestionIcon(suggestion.type)}
                    <h3 className="font-medium">{suggestion.title}</h3>
                  </div>
                  <p className="text-sm text-gray-600 mb-3">{suggestion.description}</p>
                  <div className="flex flex-wrap gap-1 mb-3">
                    {suggestion.items.map((item, itemIndex) => (
                      <Badge key={itemIndex} variant="secondary" className="text-xs">
                        {item}
                      </Badge>
                    ))}
                  </div>
                  <Button 
                    size="sm" 
                    onClick={() => onAddSuggestion(suggestion.items)}
                  >
                    Add Seasonal Items
                  </Button>
                </CardContent>
              </Card>
            ))}
        </TabsContent>

        <TabsContent value="budget" className="space-y-3">
          {suggestions
            .filter(s => s.type === 'budget')
            .map((suggestion, index) => (
              <Card key={index} className={getSuggestionColor(suggestion.type)}>
                <CardContent className="p-4">
                  <div className="flex items-center gap-2 mb-2">
                    {getSuggestionIcon(suggestion.type)}
                    <h3 className="font-medium">{suggestion.title}</h3>
                    {suggestion.savings && (
                      <Badge className="bg-green-100 text-green-800">
                        Save ${suggestion.savings.toFixed(2)}
                      </Badge>
                    )}
                  </div>
                  <p className="text-sm text-gray-600 mb-3">{suggestion.description}</p>
                  <div className="flex flex-wrap gap-1 mb-3">
                    {suggestion.items.map((item, itemIndex) => (
                      <Badge key={itemIndex} variant="secondary" className="text-xs">
                        {item}
                      </Badge>
                    ))}
                  </div>
                  <Button 
                    size="sm" 
                    onClick={() => onAddSuggestion(suggestion.items)}
                  >
                    Add Budget Items
                  </Button>
                </CardContent>
              </Card>
            ))}
        </TabsContent>

        <TabsContent value="trending" className="space-y-3">
          {suggestions
            .filter(s => s.type === 'trending')
            .map((suggestion, index) => (
              <Card key={index} className={getSuggestionColor(suggestion.type)}>
                <CardContent className="p-4">
                  <div className="flex items-center gap-2 mb-2">
                    {getSuggestionIcon(suggestion.type)}
                    <h3 className="font-medium">{suggestion.title}</h3>
                    <Badge className="bg-blue-100 text-blue-800">Trending</Badge>
                  </div>
                  <p className="text-sm text-gray-600 mb-3">{suggestion.description}</p>
                  <div className="flex flex-wrap gap-1 mb-3">
                    {suggestion.items.map((item, itemIndex) => (
                      <Badge key={itemIndex} variant="secondary" className="text-xs">
                        {item}
                      </Badge>
                    ))}
                  </div>
                  <Button 
                    size="sm" 
                    onClick={() => onAddSuggestion(suggestion.items)}
                  >
                    Add Trending Items
                  </Button>
                </CardContent>
              </Card>
            ))}
        </TabsContent>
      </Tabs>
    </div>
  )
}

export default SmartSuggestions