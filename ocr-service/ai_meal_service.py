#!/usr/bin/env python3
"""
AI Meal Generator FastAPI Service
Provides intelligent meal planning based on user preferences and machine learning
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Optional
import json
from datetime import datetime, timedelta
from ai_meal_generator import ai_meal_engine, UserPreference, MealRecord, GeneratedMeal
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Meal Generator", version="1.0.0")

# Configure CORS
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API requests/responses
class UserPreferenceRequest(BaseModel):
    user_id: str
    dietary_restrictions: List[str] = []
    favorite_ingredients: List[str] = []
    disliked_ingredients: List[str] = []
    preferred_cuisines: List[str] = []
    meal_frequency: Dict[str, int] = {"breakfast": 7, "lunch": 7, "dinner": 7, "snack": 3}
    cooking_skill: str = "intermediate"
    time_constraints: Dict[str, int] = {"breakfast": 15, "lunch": 30, "dinner": 45, "snack": 10}
    health_goals: List[str] = ["maintenance"]
    budget_range: str = "medium"
    family_size: int = 1

class MealRecordRequest(BaseModel):
    user_id: str
    meal_name: str
    ingredients: List[str]
    meal_type: str
    date: str = None
    rating: Optional[float] = None
    prep_time: Optional[int] = None
    cost: Optional[float] = None
    calories: Optional[int] = None
    enjoyed: Optional[bool] = None

class MealGenerationRequest(BaseModel):
    user_id: str
    days: int = 7
    meals_per_day: int = 3
    available_ingredients: List[str] = []
    optimize_for_waste: bool = False
    expiring_ingredients: List[Dict[str, Any]] = []
    # New waste optimization parameters
    prioritize_expiring: bool = False
    prioritize_high_quantity: bool = False
    dietary_restrictions: List[str] = []
    max_cooking_time: int = 60
    servings: int = 2
    cuisine_preference: Optional[str] = None

class WasteOptimizationRequest(BaseModel):
    user_id: str
    expiring_ingredients: List[Dict[str, Any]]

@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "message": "AI Meal Generator Service is running",
        "version": "1.0.0",
        "features": [
            "Machine Learning-based meal personalization",
            "User preference learning",
            "Waste reduction optimization",
            "Intelligent meal planning",
            "Dietary restriction adherence",
            "Cooking skill adaptation"
        ],
        "endpoints": {
            "/generate-meals": "POST - Generate personalized meal plans",
            "/learn-preference": "POST - Update user preferences",
            "/record-meal": "POST - Record a meal for learning",
            "/optimize-waste": "POST - Generate meals to reduce food waste",
            "/user-insights": "GET - Get user eating pattern insights",
            "/health": "GET - Health check"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ai-meal-generator",
        "timestamp": datetime.now().isoformat(),
        "ml_engine_status": "active"
    }

@app.post("/learn-preference")
async def update_user_preference(request: UserPreferenceRequest):
    """Update or create user preferences"""
    try:
        user_pref = UserPreference(
            user_id=request.user_id,
            dietary_restrictions=request.dietary_restrictions,
            favorite_ingredients=request.favorite_ingredients,
            disliked_ingredients=request.disliked_ingredients,
            preferred_cuisines=request.preferred_cuisines,
            meal_frequency=request.meal_frequency,
            cooking_skill=request.cooking_skill,
            time_constraints=request.time_constraints,
            health_goals=request.health_goals,
            budget_range=request.budget_range,
            family_size=request.family_size
        )
        
        ai_meal_engine.user_preferences[request.user_id] = user_pref
        ai_meal_engine._save_user_data()
        
        logger.info(f"Updated preferences for user {request.user_id}")
        
        return {
            "success": True,
            "message": f"Preferences updated for user {request.user_id}",
            "preferences": user_pref.__dict__
        }
        
    except Exception as e:
        logger.error(f"Error updating user preferences: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/record-meal")
async def record_meal(request: MealRecordRequest, background_tasks: BackgroundTasks):
    """Record a meal for machine learning"""
    try:
        meal_record = MealRecord(
            user_id=request.user_id,
            meal_name=request.meal_name,
            ingredients=request.ingredients,
            meal_type=request.meal_type,
            date=request.date or datetime.now().strftime("%Y-%m-%d"),
            rating=request.rating,
            prep_time=request.prep_time,
            cost=request.cost,
            calories=request.calories,
            enjoyed=request.enjoyed
        )
        
        # Learn from meal asynchronously to avoid blocking
        background_tasks.add_task(ai_meal_engine.learn_from_meal, meal_record)
        
        logger.info(f"Recorded meal {request.meal_name} for user {request.user_id}")
        
        return {
            "success": True,
            "message": f"Meal '{request.meal_name}' recorded successfully",
            "meal_id": f"{request.user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "learning_status": "processing"
        }
        
    except Exception as e:
        logger.error(f"Error recording meal: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-meals")
async def generate_personalized_meals(request: MealGenerationRequest):
    """Generate personalized meal plan using AI"""
    try:
        logger.info(f"Generating meal plan for user {request.user_id}")
        
        if request.optimize_for_waste and request.expiring_ingredients:
            # Optimize for waste reduction
            meals = ai_meal_engine.optimize_for_waste_reduction(
                user_id=request.user_id,
                expiring_ingredients=request.expiring_ingredients
            )
        else:
            # Standard personalized meal generation
            meals = ai_meal_engine.generate_personalized_meals(
                user_id=request.user_id,
                days=request.days,
                meals_per_day=request.meals_per_day,
                available_ingredients=request.available_ingredients
            )
        
        # Convert to dict for JSON response
        meals_dict = [meal.__dict__ for meal in meals]
        
        # Generate summary statistics
        summary = {
            "total_meals": len(meals),
            "avg_confidence": sum(meal.confidence_score for meal in meals) / len(meals) if meals else 0,
            "meal_types": {meal_type: sum(1 for meal in meals if meal.meal_type == meal_type) 
                          for meal_type in ['breakfast', 'lunch', 'dinner', 'snack']},
            "avg_prep_time": sum(meal.estimated_prep_time for meal in meals) / len(meals) if meals else 0,
            "total_estimated_cost": sum(meal.estimated_cost for meal in meals),
            "cuisines_variety": len(set(meal.cuisine for meal in meals)),
            "waste_optimized": request.optimize_for_waste
        }
        
        logger.info(f"Generated {len(meals)} meals for user {request.user_id}")
        
        return {
            "success": True,
            "meals": meals_dict,
            "summary": summary,
            "generation_timestamp": datetime.now().isoformat(),
            "user_id": request.user_id
        }
        
    except Exception as e:
        logger.error(f"Error generating meals: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/optimize-waste")
async def optimize_for_waste_reduction(request: WasteOptimizationRequest):
    """Generate meals optimized to reduce food waste"""
    try:
        logger.info(f"Optimizing meals for waste reduction for user {request.user_id}")
        
        meals = ai_meal_engine.optimize_for_waste_reduction(
            user_id=request.user_id,
            expiring_ingredients=request.expiring_ingredients
        )
        
        meals_dict = [meal.__dict__ for meal in meals]
        
        # Calculate waste reduction metrics
        expiring_items = [item['name'].lower() for item in request.expiring_ingredients]
        items_used = set()
        
        for meal in meals:
            for ingredient in meal.ingredients:
                if ingredient.lower() in expiring_items:
                    items_used.add(ingredient.lower())
        
        waste_reduction_stats = {
            "expiring_ingredients_count": len(request.expiring_ingredients),
            "ingredients_utilized": len(items_used),
            "utilization_rate": len(items_used) / len(expiring_items) if expiring_items else 0,
            "meals_generated": len(meals),
            "estimated_waste_prevented": f"${sum(item.get('cost', 2.0) for item in request.expiring_ingredients if item['name'].lower() in items_used):.2f}"
        }
        
        return {
            "success": True,
            "waste_optimized_meals": meals_dict,
            "waste_reduction_stats": waste_reduction_stats,
            "optimization_timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error optimizing for waste reduction: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/user-insights/{user_id}")
async def get_user_insights(user_id: str):
    """Get AI-generated insights about user's eating patterns"""
    try:
        insights = ai_meal_engine.get_user_insights(user_id)
        
        return {
            "success": True,
            "user_id": user_id,
            "insights": insights,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating user insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/user-preferences/{user_id}")
async def get_user_preferences(user_id: str):
    """Get current user preferences"""
    try:
        if user_id in ai_meal_engine.user_preferences:
            prefs = ai_meal_engine.user_preferences[user_id]
            return {
                "success": True,
                "user_id": user_id,
                "preferences": prefs.__dict__
            }
        else:
            return {
                "success": False,
                "message": f"No preferences found for user {user_id}",
                "default_preferences": UserPreference(user_id=user_id).__dict__
            }
            
    except Exception as e:
        logger.error(f"Error getting user preferences: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/batch-learn")
async def batch_learn_from_meals(meals: List[MealRecordRequest], background_tasks: BackgroundTasks):
    """Learn from multiple meals at once"""
    try:
        meal_records = []
        for meal_req in meals:
            meal_record = MealRecord(
                user_id=meal_req.user_id,
                meal_name=meal_req.meal_name,
                ingredients=meal_req.ingredients,
                meal_type=meal_req.meal_type,
                date=meal_req.date or datetime.now().strftime("%Y-%m-%d"),
                rating=meal_req.rating,
                prep_time=meal_req.prep_time,
                cost=meal_req.cost,
                calories=meal_req.calories,
                enjoyed=meal_req.enjoyed
            )
            meal_records.append(meal_record)
        
        # Learn from all meals asynchronously
        for meal_record in meal_records:
            background_tasks.add_task(ai_meal_engine.learn_from_meal, meal_record)
        
        return {
            "success": True,
            "message": f"Learning from {len(meal_records)} meals",
            "processed_count": len(meal_records)
        }
        
    except Exception as e:
        logger.error(f"Error in batch learning: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/meal-suggestions/{user_id}")
async def get_quick_meal_suggestions(user_id: str, meal_type: str = "lunch", count: int = 5):
    """Get quick meal suggestions for immediate use"""
    try:
        meals = ai_meal_engine.generate_personalized_meals(
            user_id=user_id,
            days=1,
            meals_per_day=count
        )
        
        # Filter by meal type
        filtered_meals = [meal for meal in meals if meal.meal_type == meal_type][:count]
        
        return {
            "success": True,
            "meal_type": meal_type,
            "suggestions": [meal.__dict__ for meal in filtered_meals],
            "count": len(filtered_meals)
        }
        
    except Exception as e:
        logger.error(f"Error getting meal suggestions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/rate-meal/{meal_id}")
async def rate_generated_meal(meal_id: str, rating: float, feedback: str = ""):
    """Rate a generated meal to improve future suggestions"""
    try:
        # Extract user_id from meal_id
        user_id = meal_id.split('_')[0] if '_' in meal_id else None
        
        if not user_id:
            raise HTTPException(status_code=400, detail="Invalid meal_id format")
        
        # This would update the ML model based on feedback
        # For now, we'll log the feedback
        logger.info(f"Meal {meal_id} rated {rating}/5 by user {user_id}: {feedback}")
        
        return {
            "success": True,
            "message": "Meal rating recorded successfully",
            "meal_id": meal_id,
            "rating": rating
        }
        
    except Exception as e:
        logger.error(f"Error rating meal: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)