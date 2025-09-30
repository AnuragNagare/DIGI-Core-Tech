from fastapi import FastAPI, HTTPException, UploadFile, File
from typing import Optional, List, Dict, Any
import base64
import io
import os
import tempfile
import requests
from PIL import Image
import json
from datetime import datetime
from food_classification_service import food_classifier
from calorie_calculation_service import calorie_calculator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="Food Classification Service", version="1.0.0")

# Configure CORS
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/classify-food")
async def classify_food_image(
    file: UploadFile = File(...), 
    extract_ingredients: bool = True
):
    """
    Classify food items in uploaded image and extract ingredients.
    
    Args:
        file: Uploaded image file
        extract_ingredients: Whether to extract detailed ingredient information
        
    Returns:
        Dictionary with classification results
    """
    try:
        # Read file content
        contents = await file.read()
        
        # Validate image
        try:
            image = Image.open(io.BytesIO(contents))
            if image.mode not in ['RGB', 'RGBA']:
                image = image.convert('RGB')
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")
        
        # Classify food items
        if extract_ingredients:
            result = food_classifier.extract_ingredients_from_meal(contents)
        else:
            result = food_classifier.classify_food(contents)
        
        if not result.get('success', False):
            return {
                "success": False,
                "error": result.get('error', 'Food classification failed'),
                "ingredients": [],
                "confidence": 0.0
            }
        
        # Format response
        response = {
            "success": True,
            "ingredients": result.get('ingredients', []),
            "confidence": result.get('confidence', 0.0),
            "total_ingredients": result.get('total_ingredients', 0),
            "processing_time": result.get('processing_time', datetime.now().isoformat()),
            "nutritional_analysis": result.get('nutritional_analysis', {}),
            "calorie_analysis": result.get('calorie_analysis', {}),
            "meal_suggestions": result.get('meal_suggestions', []),
            "dietary_labels": result.get('dietary_labels', [])
        }
        
        return response
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Food classification failed: {str(e)}",
            "ingredients": [],
            "confidence": 0.0
        }

@app.post("/classify-ingredients")
async def classify_ingredients_only(file: UploadFile = File(...)):
    """
    Simple ingredient classification without detailed analysis.
    """
    try:
        contents = await file.read()
        result = food_classifier.classify_food(contents)
        
        if not result.get('success', False):
            return {
                "success": False,
                "error": result.get('error', 'Ingredient classification failed'),
                "ingredients": []
            }
        
        # Return simplified response
        return {
            "success": True,
            "ingredients": [
                {
                    "name": ing.get('name', ''),
                    "confidence": ing.get('confidence', 0.0),
                    "category": ing.get('category', 'unknown')
                }
                for ing in result.get('ingredients', [])
            ]
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Ingredient classification failed: {str(e)}",
            "ingredients": []
        }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "service": "Food Classification Service",
        "model_loaded": food_classifier.model is not None,
        "device": str(food_classifier.device)
    }

@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "message": "Food Classification Service is running",
        "endpoints": {
            "/classify-food": "POST - Full food classification with nutritional analysis",
            "/classify-ingredients": "POST - Simple ingredient classification",
            "/health": "GET - Health check"
        },
        "features": [
            "Food item identification",
            "Ingredient extraction",
            "Nutritional analysis",
            "Meal suggestions",
            "Dietary label detection"
        ],
        "supported_categories": [
            "Fruits", "Vegetables", "Nuts & Seeds", "Grains", 
            "Proteins", "Dairy", "Herbs & Spices"
        ]
    }

@app.post("/update-portion")
async def update_portion_size(request: Dict[str, Any]):
    """
    Update portion size and recalculate precise nutrition.
    
    Args:
        request: Dictionary containing food_name, new_weight_g, original_weight_g
        
    Returns:
        Precise nutritional information with mathematical accuracy
    """
    try:
        food_name = request.get('food_name')
        new_weight_g = request.get('new_weight_g')
        original_weight_g = request.get('original_weight_g')
        
        if not all([food_name, new_weight_g, original_weight_g]):
            raise HTTPException(
                status_code=400, 
                detail="Missing required fields: food_name, new_weight_g, original_weight_g"
            )
        
        if new_weight_g <= 0:
            raise HTTPException(
                status_code=400, 
                detail="New weight must be greater than 0"
            )
        
        # Calculate precise nutrition with new weight
        precise_nutrition = calorie_calculator.calculate_precise_nutrition(food_name, new_weight_g)
        
        # Validate portion size
        validation = calorie_calculator.validate_portion_size(food_name, new_weight_g)
        
        # Calculate weight change metrics
        weight_change_g = new_weight_g - original_weight_g
        weight_change_percent = (weight_change_g / original_weight_g) * 100
        
        return {
            "success": True,
            "food_name": food_name,
            "original_weight_g": original_weight_g,
            "updated_weight_g": new_weight_g,
            "weight_change_g": round(weight_change_g, 1),
            "weight_change_percent": round(weight_change_percent, 1),
            "precise_nutrition": precise_nutrition,
            "validation": validation,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update portion size: {str(e)}"
        )

@app.get("/test")
async def test_classification():
    """Test endpoint with sample food classification"""
    try:
        # Create a sample result
        sample_result = {
            "success": True,
            "ingredients": [
                {
                    "name": "apple",
                    "confidence": 0.95,
                    "category": "fruits",
                    "nutritional_info": ["vitamin_c", "fiber", "antioxidants"]
                },
                {
                    "name": "carrot",
                    "confidence": 0.88,
                    "category": "vegetables", 
                    "nutritional_info": ["vitamin_a", "beta_carotene", "fiber"]
                }
            ],
            "confidence": 0.92,
            "total_ingredients": 2,
            "processing_time": datetime.now().isoformat(),
            "nutritional_analysis": {
                "total_ingredients": 2,
                "average_confidence": 0.92,
                "detected_nutrients": ["vitamin_c", "fiber", "antioxidants", "vitamin_a", "beta_carotene"],
                "health_score": 9.2,
                "dietary_balance": "well-balanced"
            },
            "meal_suggestions": [
                "Great for a healthy salad or stir-fry!",
                "Perfect for a fruit smoothie or dessert!"
            ],
            "dietary_labels": ["vegetable-rich", "fruit-included"]
        }
        
        return sample_result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
