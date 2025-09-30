import { NextRequest, NextResponse } from 'next/server'

interface UpdatePortionRequest {
  foodName: string
  newWeight: number
  originalWeight: number
}

interface PreciseNutritionResponse {
  calories: number
  protein: number
  carbs: number
  fat: number
  fiber: number
  portion_size_g: number
  calorie_accuracy: number
  calories_from_protein: number
  calories_from_carbs: number
  calories_from_fat: number
  total_calculated_calories: number
  validation: {
    valid: boolean
    typical_portion_g: number
    deviation_percent: number
    recommendation: string
  }
}

export async function POST(request: NextRequest) {
  try {
    const body: UpdatePortionRequest = await request.json()
    const { foodName, newWeight, originalWeight } = body

    if (!foodName || !newWeight || newWeight <= 0) {
      return NextResponse.json(
        { error: 'Invalid food name or weight' },
        { status: 400 }
      )
    }

    // Call the Python service for precise nutrition calculation
    const pythonServiceUrl = process.env.FOOD_SERVICE_URL || 'http://localhost:8001'
    
    const response = await fetch(`${pythonServiceUrl}/update-portion`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        food_name: foodName,
        new_weight_g: newWeight,
        original_weight_g: originalWeight
      }),
    })

    if (!response.ok) {
      throw new Error(`Python service error: ${response.statusText}`)
    }

    const preciseNutrition: PreciseNutritionResponse = await response.json()

    return NextResponse.json({
      success: true,
      food_name: foodName,
      original_weight_g: originalWeight,
      updated_weight_g: newWeight,
      weight_change_g: newWeight - originalWeight,
      weight_change_percent: ((newWeight - originalWeight) / originalWeight) * 100,
      precise_nutrition: preciseNutrition,
      timestamp: new Date().toISOString()
    })

  } catch (error) {
    console.error('Error updating portion size:', error)
    return NextResponse.json(
      { 
        error: 'Failed to update portion size',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}
