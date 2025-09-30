import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Progress } from '@/components/ui/progress'
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  Legend
} from 'recharts'
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  ShoppingCart,
  Calendar,
  Target,
  Award,
  Activity,
  PieChart as PieChartIcon,
  BarChart3
} from 'lucide-react'

interface ShoppingMetrics {
  totalSpent: number
  itemsBought: number
  averageSpentPerTrip: number
  budgetUtilization: number
  categoryBreakdown: { category: string; amount: number; percentage: number }[]
  spendingTrend: { month: string; amount: number }[]
  topItems: { item: string; count: number; totalSpent: number }[]
  budgetComparison: { budget: number; spent: number; remaining: number }
  savingsAchieved: number
  shoppingFrequency: number
}

interface ShoppingAnalyticsProps {
  userId: string
  timeRange: 'week' | 'month' | 'quarter' | 'year'
  onTimeRangeChange: (range: 'week' | 'month' | 'quarter' | 'year') => void
}

const ShoppingAnalytics: React.FC<ShoppingAnalyticsProps> = ({
  userId,
  timeRange,
  onTimeRangeChange
}) => {
  const [metrics, setMetrics] = useState<ShoppingMetrics | null>(null)
  const [loading, setLoading] = useState(false)
  const [insights, setInsights] = useState<string[]>([])

  // Colors for charts
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D']

  // Fetch analytics data
  const fetchAnalytics = async () => {
    setLoading(true)
    try {
      const response = await fetch(`/api/shopping/analytics/${userId}?range=${timeRange}`)
      const data = await response.json()

      if (data.success) {
        setMetrics(data.metrics)
        generateInsights(data.metrics)
      }
    } catch (error) {
      console.error('Failed to fetch shopping analytics:', error)
    } finally {
      setLoading(false)
    }
  }

  // Generate AI insights
  const generateInsights = (metricsData: ShoppingMetrics) => {
    const newInsights: string[] = []

    // Budget insights
    if (metricsData.budgetUtilization > 90) {
      newInsights.push('🎯 You\'re close to your budget limit. Consider prioritizing essential items.')
    } else if (metricsData.budgetUtilization < 50) {
      newInsights.push('💰 You have significant budget room. Good opportunity for bulk buying or trying new items.')
    }

    // Spending pattern insights
    if (metricsData.averageSpentPerTrip > 50) {
      newInsights.push('🛒 Your average trip cost is high. Consider making a detailed list to avoid impulse purchases.')
    }

    // Category insights
    const topCategory = metricsData.categoryBreakdown[0]
    if (topCategory && topCategory.percentage > 40) {
      newInsights.push(`📊 ${topCategory.category} accounts for ${topCategory.percentage}% of your spending. Consider diversifying.`)
    }

    // Savings insights
    if (metricsData.savingsAchieved > 0) {
      newInsights.push(`🎉 You've saved $${metricsData.savingsAchieved.toFixed(2)} this ${timeRange} through smart shopping!`)
    }

    // Frequency insights
    if (metricsData.shoppingFrequency > 3) {
      newInsights.push('🔄 You shop frequently. Consolidating trips could save time and reduce impulse purchases.')
    }

    setInsights(newInsights)
  }

  // Format currency
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount)
  }

  // Get trend direction
  const getTrendDirection = (current: number, previous: number) => {
    if (current > previous) return { icon: TrendingUp, color: 'text-green-600', text: 'increase' }
    if (current < previous) return { icon: TrendingDown, color: 'text-red-600', text: 'decrease' }
    return { icon: Activity, color: 'text-gray-600', text: 'stable' }
  }

  useEffect(() => {
    fetchAnalytics()
  }, [userId, timeRange])

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className="h-32 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  if (!metrics) {
    return (
      <Card>
        <CardContent className="p-8 text-center">
          <BarChart3 className="w-12 h-12 mx-auto mb-3 opacity-50" />
          <p className="text-gray-500">No analytics data available.</p>
          <Button onClick={fetchAnalytics} className="mt-3" size="sm">
            Load Analytics
          </Button>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="w-5 h-5" />
                Shopping Analytics Dashboard
              </CardTitle>
              <CardDescription>
                Comprehensive insights into your shopping patterns and spending habits
              </CardDescription>
            </div>
            
            <div className="flex gap-2">
              {(['week', 'month', 'quarter', 'year'] as const).map((range) => (
                <Button
                  key={range}
                  variant={timeRange === range ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => onTimeRangeChange(range)}
                  className="capitalize"
                >
                  {range}
                </Button>
              ))}
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Spent</p>
                <p className="text-2xl font-bold">{formatCurrency(metrics.totalSpent)}</p>
              </div>
              <DollarSign className="w-8 h-8 text-green-600" />
            </div>
            <div className="mt-2">
              <Progress value={metrics.budgetUtilization} className="h-2" />
              <p className="text-xs text-gray-500 mt-1">
                {metrics.budgetUtilization.toFixed(1)}% of budget used
              </p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Items Purchased</p>
                <p className="text-2xl font-bold">{metrics.itemsBought}</p>
              </div>
              <ShoppingCart className="w-8 h-8 text-blue-600" />
            </div>
            <p className="text-xs text-gray-500 mt-2">
              Avg: {(metrics.itemsBought / Math.max(metrics.shoppingFrequency, 1)).toFixed(1)} items/trip
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Avg Per Trip</p>
                <p className="text-2xl font-bold">{formatCurrency(metrics.averageSpentPerTrip)}</p>
              </div>
              <Target className="w-8 h-8 text-purple-600" />
            </div>
            <p className="text-xs text-gray-500 mt-2">
              {metrics.shoppingFrequency} shopping trips
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Savings Achieved</p>
                <p className="text-2xl font-bold text-green-600">
                  {formatCurrency(metrics.savingsAchieved)}
                </p>
              </div>
              <Award className="w-8 h-8 text-yellow-600" />
            </div>
            <p className="text-xs text-gray-500 mt-2">
              Smart shopping rewards
            </p>
          </CardContent>
        </Card>
      </div>

      {/* AI Insights */}
      {insights.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="w-5 h-5" />
              🤖 AI Shopping Insights
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {insights.map((insight, index) => (
                <div key={index} className="flex items-start gap-3 p-3 bg-blue-50 rounded-lg">
                  <div className="w-2 h-2 bg-blue-600 rounded-full mt-2 flex-shrink-0"></div>
                  <p className="text-sm text-blue-800">{insight}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Charts */}
      <Tabs defaultValue="spending" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="spending">Spending Trend</TabsTrigger>
          <TabsTrigger value="categories">Categories</TabsTrigger>
          <TabsTrigger value="items">Top Items</TabsTrigger>
          <TabsTrigger value="budget">Budget Analysis</TabsTrigger>
        </TabsList>

        <TabsContent value="spending" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Spending Trend</CardTitle>
              <CardDescription>Your spending pattern over time</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={metrics.spendingTrend}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip formatter={(value) => [formatCurrency(Number(value)), 'Amount']} />
                  <Line 
                    type="monotone" 
                    dataKey="amount" 
                    stroke="#8884d8" 
                    strokeWidth={3}
                    dot={{ fill: '#8884d8', strokeWidth: 2, r: 4 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="categories" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle>Spending by Category</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={metrics.categoryBreakdown}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ category, percentage }) => `${category}: ${percentage}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="amount"
                    >
                      {metrics.categoryBreakdown.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => formatCurrency(Number(value))} />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Category Breakdown</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {metrics.categoryBreakdown.map((category, index) => (
                    <div key={category.category} className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div 
                          className="w-3 h-3 rounded-full bg-blue-500"
                        />
                        <span className="font-medium">{category.category}</span>
                      </div>
                      <div className="text-right">
                        <p className="font-medium">{formatCurrency(category.amount)}</p>
                        <p className="text-xs text-gray-500">{category.percentage}%</p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="items" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Most Purchased Items</CardTitle>
              <CardDescription>Items you buy most frequently</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {metrics.topItems.map((item, index) => (
                  <div key={item.item} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center gap-3">
                      <Badge variant="outline" className="w-8 h-8 rounded-full p-0 flex items-center justify-center">
                        {index + 1}
                      </Badge>
                      <div>
                        <p className="font-medium">{item.item}</p>
                        <p className="text-sm text-gray-500">{item.count} purchases</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-medium">{formatCurrency(item.totalSpent)}</p>
                      <p className="text-xs text-gray-500">
                        {formatCurrency(item.totalSpent / item.count)} avg
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="budget" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Budget Analysis</CardTitle>
              <CardDescription>How you're tracking against your budget</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <div className="flex items-center justify-between text-lg font-medium">
                  <span>Budget Progress</span>
                  <span>{formatCurrency(metrics.budgetComparison.spent)} / {formatCurrency(metrics.budgetComparison.budget)}</span>
                </div>
                
                <Progress value={metrics.budgetUtilization} className="h-3" />
                
                <div className="grid grid-cols-3 gap-4 text-center">
                  <div className="p-3 bg-blue-50 rounded-lg">
                    <p className="text-sm text-gray-600">Budget</p>
                    <p className="text-lg font-bold text-blue-600">
                      {formatCurrency(metrics.budgetComparison.budget)}
                    </p>
                  </div>
                  <div className="p-3 bg-red-50 rounded-lg">
                    <p className="text-sm text-gray-600">Spent</p>
                    <p className="text-lg font-bold text-red-600">
                      {formatCurrency(metrics.budgetComparison.spent)}
                    </p>
                  </div>
                  <div className="p-3 bg-green-50 rounded-lg">
                    <p className="text-sm text-gray-600">Remaining</p>
                    <p className="text-lg font-bold text-green-600">
                      {formatCurrency(metrics.budgetComparison.remaining)}
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

export default ShoppingAnalytics