import { NextResponse } from 'next/server'
import type { ApiResponse, FamilyMeal } from '@/lib/types'
import { FamilyMealService } from '@/lib/family-meal-service'

export async function GET(request: Request): Promise<NextResponse<ApiResponse<FamilyMeal[]>>> {
  try {
    const { searchParams } = new URL(request.url)
    const familyId = searchParams.get('familyId')

    if (!familyId) {
      return NextResponse.json({ success: false, error: 'Family ID required' }, { status: 400 })
    }

    const meals = await FamilyMealService.getFamilyMeals(familyId)
    return NextResponse.json({ success: true, data: meals })
  } catch (error) {
    return NextResponse.json({ 
      success: false, 
      error: error instanceof Error ? error.message : 'Failed to get family meals' 
    }, { status: 500 })
  }
}

export async function POST(request: Request): Promise<NextResponse<ApiResponse<FamilyMeal>>> {
  try {
    const body = await request.json()
    const { familyId, name, description, date, time, createdBy, ingredients } = body

    if (!familyId || !name || !date || !time || !createdBy) {
      return NextResponse.json({ 
        success: false, 
        error: 'Family ID, name, date, time, and createdBy are required' 
      }, { status: 400 })
    }

    const meal = await FamilyMealService.createFamilyMeal(
      familyId,
      name,
      description || '',
      date,
      time,
      createdBy,
      ingredients || []
    )

    return NextResponse.json({ success: true, data: meal })
  } catch (error) {
    return NextResponse.json({ 
      success: false, 
      error: error instanceof Error ? error.message : 'Failed to create family meal' 
    }, { status: 500 })
  }
}
