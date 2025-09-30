import { NextResponse } from 'next/server';

interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

interface FoodIngredient {
  name: string;
  confidence: number;
  category: string;
  nutritional_info: string[];
}

interface CalorieAnalysis {
  total_calories: number;
  total_protein: number;
  total_carbs: number;
  total_fat: number;
  total_fiber: number;
  total_weight_g: number;
  calories_per_100g: number;
  detailed_breakdown: Array<{
    name: string;
    portion_size_g: number;
    calories: number;
    protein: number;
    carbs: number;
    fat: number;
    fiber: number;
    confidence: number;
  }>;
  meal_type: string;
  nutritional_quality: {
    quality_score: number;
    quality_rating: string;
    protein_percentage: number;
    fat_percentage: number;
    fiber_content: number;
    recommendations: string[];
  };
  dietary_recommendations: string[];
}

interface FoodClassificationResult {
  ingredients: FoodIngredient[];
  confidence: number;
  total_ingredients: number;
  processing_time: string;
  nutritional_analysis: {
    total_ingredients: number;
    average_confidence: number;
    detected_nutrients: string[];
    health_score: number;
    dietary_balance: string;
  };
  calorie_analysis: CalorieAnalysis;
  meal_suggestions: string[];
  dietary_labels: string[];
}

export async function POST(request: Request) {
  console.log('Received food classification request');

  try {
    const body = await request.json().catch((e) => {
      console.error('Error parsing request body:', e);
      return {};
    }) as { imageDataUrl?: string };

    if (!body.imageDataUrl) {
      console.error('No imageDataUrl provided in request');
      return NextResponse.json(
        { success: false, error: 'imageDataUrl required' } as ApiResponse<any>,
        { status: 400 }
      );
    }

    console.log('Calling Python food classification service');

    // The Python service lives at this URL
    const foodServiceUrl = process.env.NEXT_PUBLIC_FOOD_SERVICE_URL || 'http://localhost:8001';

    // Convert base64 to buffer
    const base64Data = body.imageDataUrl.split(',')[1];
    const imageBuffer = Buffer.from(base64Data, 'base64');

    // Create proper multipart form data
    const boundary = '----formdata-boundary-' + Date.now();
    const CRLF = '\r\n';

    let postData = '';
    postData += `--${boundary}${CRLF}`;
    postData += `Content-Disposition: form-data; name="file"; filename="food_image.jpg"${CRLF}`;
    postData += `Content-Type: image/jpeg${CRLF}${CRLF}`;

    const postBuffer = Buffer.concat([
      Buffer.from(postData, 'utf8'),
      imageBuffer,
      Buffer.from(`${CRLF}--${boundary}${CRLF}`, 'utf8'),
      Buffer.from(`Content-Disposition: form-data; name="extract_ingredients"${CRLF}${CRLF}`, 'utf8'),
      Buffer.from('true', 'utf8'),
      Buffer.from(`${CRLF}--${boundary}--${CRLF}`, 'utf8')
    ]);

    const response = await fetch(`${foodServiceUrl}/classify-food`, {
      method: 'POST',
      headers: {
        'Content-Type': `multipart/form-data; boundary=${boundary}`,
        'Content-Length': postBuffer.length.toString(),
      },
      body: postBuffer,
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Food classification service returned error status:', response.status, errorText);
      return NextResponse.json({ success: false, error: `Food classification failed: ${errorText}` }, { status: 500 });
    }

    const result = await response.json();

    if (!result.success) {
      console.error('Food classification service returned success=false:', result.error);
      return NextResponse.json({ success: false, error: result.error || 'Food classification failed in Python service' }, { status: 500 });
    }

    // Process the result for the frontend
    const processedResult: FoodClassificationResult = {
      ingredients: result.ingredients || [],
      confidence: result.confidence || 0,
      total_ingredients: result.total_ingredients || 0,
      processing_time: result.processing_time || new Date().toISOString(),
      nutritional_analysis: result.nutritional_analysis || {
        total_ingredients: 0,
        average_confidence: 0,
        detected_nutrients: [],
        health_score: 0,
        dietary_balance: 'unknown'
      },
      calorie_analysis: result.calorie_analysis || {
        total_calories: 0,
        total_protein: 0,
        total_carbs: 0,
        total_fat: 0,
        total_fiber: 0,
        total_weight_g: 0,
        calories_per_100g: 0,
        detailed_breakdown: [],
        meal_type: 'unknown',
        nutritional_quality: {
          quality_score: 0,
          quality_rating: 'unknown',
          protein_percentage: 0,
          fat_percentage: 0,
          fiber_content: 0,
          recommendations: []
        },
        dietary_recommendations: []
      },
      meal_suggestions: result.meal_suggestions || [],
      dietary_labels: result.dietary_labels || []
    };

    return NextResponse.json({ success: true, data: processedResult });

  } catch (error) {
    console.error('Error processing food classification:', error);
    const errorMessage = error instanceof Error ? error.message : 'Failed to process food classification';
    return NextResponse.json(
      { success: false, error: errorMessage } as ApiResponse<any>,
      { status: 500 }
    );
  }
}