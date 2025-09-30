import { NextRequest, NextResponse } from 'next/server'

// Complete AI Shopping List API Integration
export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url)
  const userId = searchParams.get('userId')
  const action = searchParams.get('action')

  if (!userId) {
    return NextResponse.json(
      { success: false, error: 'User ID is required' },
      { status: 400 }
    )
  }

  try {
    switch (action) {
      case 'predictions':
        return handlePredictions(userId, searchParams)
      case 'suggestions':
        return handleSuggestions(userId, searchParams)
      case 'analytics':
        return handleAnalytics(userId, searchParams)
      default:
        return NextResponse.json(
          { success: false, error: 'Invalid action' },
          { status: 400 }
        )
    }
  } catch (error) {
    console.error('AI Shopping API error:', error)
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    )
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { userId, action, data } = body

    if (!userId || !action) {
      return NextResponse.json(
        { success: false, error: 'User ID and action are required' },
        { status: 400 }
      )
    }

    switch (action) {
      case 'feedback':
        return handleFeedback(userId, data)
      case 'update_preferences':
        return handleUpdatePreferences(userId, data)
      case 'save_shopping_list':
        return handleSaveShoppingList(userId, data)
      default:
        return NextResponse.json(
          { success: false, error: 'Invalid action' },
          { status: 400 }
        )
    }
  } catch (error) {
    console.error('AI Shopping API POST error:', error)
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    )
  }
}

// Handle AI predictions
async function handlePredictions(userId: string, searchParams: URLSearchParams) {
  const currentItems = searchParams.get('currentItems')?.split(',') || []
  const budget = parseFloat(searchParams.get('budget') || '0')
  
  // Call ML service for predictions
  const mlResponse = await fetch(`${process.env.ML_SERVICE_URL}/api/shopping/ai-predict`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id: userId,
      current_items: currentItems,
      budget,
      preferences: await getUserPreferences(userId)
    })
  })

  if (!mlResponse.ok) {
    throw new Error('ML service unavailable')
  }

  const predictions = await mlResponse.json()
  
  return NextResponse.json({
    success: true,
    predictions: predictions.predictions || [],
    confidence_scores: predictions.confidence_scores || {},
    category_suggestions: predictions.category_suggestions || [],
    seasonal_recommendations: predictions.seasonal_recommendations || [],
    replenishment_suggestions: predictions.replenishment_suggestions || []
  })
}

// Handle smart suggestions
async function handleSuggestions(userId: string, searchParams: URLSearchParams) {
  const month = searchParams.get('month') || new Date().toLocaleString('default', { month: 'long' })
  const budget = parseFloat(searchParams.get('budget') || '0')

  // Generate smart suggestions
  const suggestions = {
    seasonal: await getSeasonalSuggestions(month),
    budget: await getBudgetFriendlySuggestions(budget),
    trending: await getTrendingSuggestions(),
    frequent: await getFrequentItems(userId)
  }

  return NextResponse.json({
    success: true,
    suggestions
  })
}

// Handle analytics
async function handleAnalytics(userId: string, searchParams: URLSearchParams) {
  const timeRange = searchParams.get('range') || 'month'
  
  // Get user shopping history and generate analytics
  const shoppingHistory = await getShoppingHistory(userId, timeRange)
  const analytics = await generateAnalytics(shoppingHistory)

  return NextResponse.json({
    success: true,
    metrics: analytics
  })
}

// Handle user feedback
async function handleFeedback(userId: string, data: any) {
  const { item, action, rating } = data
  
  // Store feedback for ML model improvement
  await storeFeedback(userId, {
    item,
    action, // 'accepted', 'rejected', 'modified'
    rating,
    timestamp: new Date().toISOString()
  })

  return NextResponse.json({ success: true })
}

// Handle preference updates
async function handleUpdatePreferences(userId: string, data: any) {
  await updateUserPreferences(userId, data)
  return NextResponse.json({ success: true })
}

// Handle saving shopping list
async function handleSaveShoppingList(userId: string, data: any) {
  const { items, metadata } = data
  
  await saveShoppingList(userId, {
    items,
    metadata,
    saved_at: new Date().toISOString()
  })

  return NextResponse.json({ success: true })
}

// Helper functions
async function getUserPreferences(userId: string) {
  // Mock preferences - in real app, fetch from database
  return {
    dietary_restrictions: [],
    preferred_brands: [],
    budget_preference: 'medium',
    shopping_frequency: 'weekly'
  }
}

async function getSeasonalSuggestions(month: string) {
  const seasonalItems: Record<string, string[]> = {
    'December': ['Hot chocolate', 'Holiday cookies', 'Cranberries', 'Eggnog'],
    'January': ['Soup ingredients', 'Citrus fruits', 'Root vegetables'],
    'February': ['Valentine chocolate', 'Strawberries', 'Red wine'],
    'March': ['Spring vegetables', 'Easter eggs', 'Lamb'],
    'April': ['Spring cleaning supplies', 'Fresh herbs', 'Asparagus'],
    'May': ['Grilling supplies', 'Fresh berries', 'Mother\'s Day flowers'],
    'June': ['BBQ sauce', 'Summer fruits', 'Sunscreen'],
    'July': ['Picnic supplies', 'Ice cream', 'Watermelon'],
    'August': ['School supplies', 'Peaches', 'Corn'],
    'September': ['Apple cider', 'Pumpkin', 'Back to school snacks'],
    'October': ['Halloween candy', 'Squash', 'Cinnamon'],
    'November': ['Turkey', 'Cranberry sauce', 'Thanksgiving sides']
  }

  return seasonalItems[month] || []
}

async function getBudgetFriendlySuggestions(budget: number) {
  const budgetItems = [
    'Generic brand cereals',
    'Seasonal produce',
    'Bulk rice and beans',
    'Store brand pasta',
    'Frozen vegetables',
    'Canned tomatoes',
    'Oatmeal',
    'Bananas'
  ]
  
  return budgetItems.slice(0, Math.min(5, Math.floor(budget / 10)))
}

async function getTrendingSuggestions() {
  return [
    'Plant-based milk alternatives',
    'Air fryer accessories',
    'Kombucha',
    'Cauliflower rice',
    'Protein bars',
    'Matcha powder'
  ]
}

async function getFrequentItems(userId: string) {
  // Mock frequent items - in real app, analyze purchase history
  return [
    'Milk',
    'Bread',
    'Eggs',
    'Bananas',
    'Coffee'
  ]
}

async function getShoppingHistory(userId: string, timeRange: string) {
  // Mock shopping history - in real app, fetch from database
  const mockHistory = {
    week: { totalSpent: 45.32, itemsBought: 12, trips: 2 },
    month: { totalSpent: 180.50, itemsBought: 48, trips: 8 },
    quarter: { totalSpent: 540.75, itemsBought: 144, trips: 24 },
    year: { totalSpent: 2163.00, itemsBought: 576, trips: 96 }
  }

  return mockHistory[timeRange as keyof typeof mockHistory] || mockHistory.month
}

async function generateAnalytics(history: any) {
  return {
    totalSpent: history.totalSpent,
    itemsBought: history.itemsBought,
    averageSpentPerTrip: history.totalSpent / history.trips,
    budgetUtilization: 75.5,
    categoryBreakdown: [
      { category: 'Groceries', amount: history.totalSpent * 0.6, percentage: 60 },
      { category: 'Household', amount: history.totalSpent * 0.2, percentage: 20 },
      { category: 'Personal Care', amount: history.totalSpent * 0.15, percentage: 15 },
      { category: 'Other', amount: history.totalSpent * 0.05, percentage: 5 }
    ],
    spendingTrend: [
      { month: 'Jan', amount: history.totalSpent * 0.8 },
      { month: 'Feb', amount: history.totalSpent * 0.9 },
      { month: 'Mar', amount: history.totalSpent * 1.1 },
      { month: 'Apr', amount: history.totalSpent }
    ],
    topItems: [
      { item: 'Milk', count: 8, totalSpent: 24.00 },
      { item: 'Bread', count: 6, totalSpent: 18.00 },
      { item: 'Eggs', count: 5, totalSpent: 15.00 }
    ],
    budgetComparison: {
      budget: 200,
      spent: history.totalSpent,
      remaining: 200 - history.totalSpent
    },
    savingsAchieved: 25.50,
    shoppingFrequency: history.trips
  }
}

async function storeFeedback(userId: string, feedback: any) {
  // Store feedback in database for ML model improvement
  console.log(`Storing feedback for user ${userId}:`, feedback)
}

async function updateUserPreferences(userId: string, preferences: any) {
  // Update user preferences in database
  console.log(`Updating preferences for user ${userId}:`, preferences)
}

async function saveShoppingList(userId: string, listData: any) {
  // Save shopping list to database
  console.log(`Saving shopping list for user ${userId}:`, listData)
}