import { NextResponse } from 'next/server'
import type { ApiResponse, NotificationPreferences } from '@/lib/types'
import { FamilyMealService } from '@/lib/family-meal-service'

export async function GET(request: Request): Promise<NextResponse<ApiResponse<NotificationPreferences>>> {
  try {
    const { searchParams } = new URL(request.url)
    const userId = searchParams.get('userId')

    if (!userId) {
      return NextResponse.json({ success: false, error: 'User ID required' }, { status: 400 })
    }

    const preferences = await FamilyMealService.getNotificationPreferences(userId)
    
    if (!preferences) {
      return NextResponse.json({ 
        success: false, 
        error: 'Notification preferences not found' 
      }, { status: 404 })
    }

    return NextResponse.json({ success: true, data: preferences })
  } catch (error) {
    return NextResponse.json({ 
      success: false, 
      error: error instanceof Error ? error.message : 'Failed to get notification preferences' 
    }, { status: 500 })
  }
}

export async function POST(request: Request): Promise<NextResponse<ApiResponse<NotificationPreferences>>> {
  try {
    const body = await request.json()
    const { userId, ...preferences } = body

    if (!userId) {
      return NextResponse.json({ 
        success: false, 
        error: 'User ID is required' 
      }, { status: 400 })
    }

    const updatedPreferences = await FamilyMealService.updateNotificationPreferences(userId, preferences)
    return NextResponse.json({ success: true, data: updatedPreferences })
  } catch (error) {
    return NextResponse.json({ 
      success: false, 
      error: error instanceof Error ? error.message : 'Failed to update notification preferences' 
    }, { status: 500 })
  }
}
