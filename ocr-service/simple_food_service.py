#!/usr/bin/env python3
"""
Simple Food Classification Service
Basic food classification without heavy ML dependencies
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from typing import Optional, List, Dict, Any
import base64
import io
import os
import json
from datetime import datetime
from PIL import Image
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="Simple Food Classification Service", version="1.0.0")

# Configure CORS
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple food categories and items
FOOD_DATABASE = {
    "fruits": ["apple", "banana", "orange", "grape", "strawberry", "blueberry", "mango", "pineapple"],
    "vegetables": ["tomato", "carrot", "broccoli", "spinach", "lettuce", "onion", "potato", "pepper"],
    "proteins": ["chicken", "beef", "fish", "eggs", "tofu", "beans", "pork", "turkey"],
    "dairy": ["milk", "cheese", "yogurt", "butter", "cream"],
    "grains": ["rice", "bread", "pasta", "oats", "quinoa", "wheat", "barley"],
    "snacks": ["chips", "cookies", "crackers", "nuts", "popcorn"]
}

@app.get("/")
async def root():
    return {
        "service": "Simple Food Classification Service",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "/classify-food": "POST - Classify food items in images",
            "/food-categories": "GET - List all food categories",
            "/health": "GET - Health check"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/food-categories")
async def get_food_categories():
    """Get all available food categories and items"""
    return {
        "categories": FOOD_DATABASE,
        "total_categories": len(FOOD_DATABASE),
        "total_items": sum(len(items) for items in FOOD_DATABASE.values())
    }

@app.post("/classify-food")
async def classify_food_image(
    file: UploadFile = File(...), 
    extract_ingredients: bool = True
):
    """
    Classify food items in uploaded image (mock classification for now).
    
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
            image.verify()  # Verify it's a valid image
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")
        
        # Mock classification result (in a real implementation, this would use ML models)
        # For now, return a sample classification
        mock_results = {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "image_info": {
                "filename": file.filename,
                "size": len(contents),
                "format": image.format if hasattr(image, 'format') else "unknown"
            },
            "classification": {
                "detected_items": [
                    {
                        "name": "apple",
                        "category": "fruits",
                        "confidence": 0.85,
                        "bounding_box": [100, 100, 200, 200]
                    },
                    {
                        "name": "banana",
                        "category": "fruits", 
                        "confidence": 0.78,
                        "bounding_box": [250, 150, 350, 280]
                    }
                ],
                "total_items": 2,
                "processing_time_ms": 150
            }
        }
        
        if extract_ingredients:
            mock_results["ingredients"] = {
                "primary": ["apple", "banana"],
                "nutritional_info": {
                    "apple": {"calories": 95, "carbs": 25, "fiber": 4},
                    "banana": {"calories": 105, "carbs": 27, "fiber": 3}
                }
            }
        
        return mock_results
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")

@app.post("/analyze-nutrition")
async def analyze_nutrition(food_items: List[str]):
    """
    Analyze nutrition information for a list of food items.
    
    Args:
        food_items: List of food item names
        
    Returns:
        Nutrition analysis
    """
    # Mock nutrition data
    nutrition_db = {
        "apple": {"calories": 95, "carbs": 25, "protein": 0.5, "fat": 0.3, "fiber": 4},
        "banana": {"calories": 105, "carbs": 27, "protein": 1.3, "fat": 0.4, "fiber": 3},
        "chicken": {"calories": 165, "carbs": 0, "protein": 31, "fat": 3.6, "fiber": 0},
        "rice": {"calories": 130, "carbs": 28, "protein": 2.7, "fat": 0.3, "fiber": 0.4}
    }
    
    total_nutrition = {"calories": 0, "carbs": 0, "protein": 0, "fat": 0, "fiber": 0}
    item_details = []
    
    for item in food_items:
        item_lower = item.lower()
        if item_lower in nutrition_db:
            nutrition = nutrition_db[item_lower]
            item_details.append({
                "name": item,
                "nutrition": nutrition,
                "found": True
            })
            
            for key in total_nutrition:
                total_nutrition[key] += nutrition[key]
        else:
            item_details.append({
                "name": item,
                "nutrition": None,
                "found": False
            })
    
    return {
        "success": True,
        "total_nutrition": total_nutrition,
        "items": item_details,
        "summary": {
            "total_items": len(food_items),
            "found_items": len([item for item in item_details if item["found"]]),
            "missing_items": len([item for item in item_details if not item["found"]])
        }
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Simple Food Classification Service...")
    print("📝 API Documentation: http://localhost:8001/docs")
    print("🔍 Health Check: http://localhost:8001/health")
    
    uvicorn.run(app, host="0.0.0.0", port=8001)