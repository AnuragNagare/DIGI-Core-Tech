import { NextResponse } from 'next/server'
import type { ApiResponse, FamilyMeal } from '@/lib/types'
import { FamilyMealService } from '@/lib/family-meal-service'

export async function PATCH(
  request: Request,
  { params }: { params: { id: string } }
): Promise<NextResponse<ApiResponse<FamilyMeal>>> {
  try {
    const body = await request.json()
    const { status } = body
    const mealId = params.id

    if (!status) {
      return NextResponse.json({ 
        success: false, 
        error: 'Status is required' 
      }, { status: 400 })
    }

    const validStatuses = ['planned', 'cooking', 'completed', 'cancelled']
    if (!validStatuses.includes(status)) {
      return NextResponse.json({ 
        success: false, 
        error: 'Invalid status. Must be one of: planned, cooking, completed, cancelled' 
      }, { status: 400 })
    }

    const meal = await FamilyMealService.updateMealStatus(mealId, status)
    
    if (!meal) {
      return NextResponse.json({ 
        success: false, 
        error: 'Meal not found' 
      }, { status: 404 })
    }

    return NextResponse.json({ success: true, data: meal })
  } catch (error) {
    return NextResponse.json({ 
      success: false, 
      error: error instanceof Error ? error.message : 'Failed to update meal status' 
    }, { status: 500 })
  }
}
