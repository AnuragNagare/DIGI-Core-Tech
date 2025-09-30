#!/usr/bin/env python3
"""
AI Shopping API Integration
FastAPI endpoints for the AI Shopping List service
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
import uvicorn
import json
from datetime import datetime

# Import our AI Shopping Service
from ai_shopping_service import AIShoppingService

# Initialize FastAPI app
app = FastAPI(
    title="AI Shopping List API",
    description="Intelligent shopping list generation using machine learning",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI Shopping Service
ai_shopping_service = AIShoppingService()

# Pydantic Models
class InventoryItem(BaseModel):
    name: str
    quantity: str
    category: str
    unit: str = "piece"
    daysLeft: Optional[int] = None
    price: Optional[float] = None

class ShoppingHistoryItem(BaseModel):
    name: str
    category: str
    brand: Optional[str] = None
    price: Optional[float] = None
    quantity: int = 1

class ShoppingHistoryEntry(BaseModel):
    date: str
    items: List[ShoppingHistoryItem]
    total_cost: float = 0.0
    store: Optional[str] = None

class ShoppingListRequest(BaseModel):
    user_id: str
    current_inventory: List[InventoryItem]
    shopping_history: List[ShoppingHistoryEntry]
    budget_limit: Optional[float] = None
    preferences: Optional[Dict[str, Any]] = None

class FeedbackRequest(BaseModel):
    user_id: str
    item_name: str
    feedback: str  # 'positive', 'negative', 'neutral'
    reason: Optional[str] = None

class PatternAnalysisRequest(BaseModel):
    user_id: str
    shopping_history: List[ShoppingHistoryEntry]

# API Endpoints

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "AI Shopping List API",
        "version": "1.0.0",
        "endpoints": {
            "generate": "/api/shopping/ai-predict",
            "patterns": "/api/shopping/patterns",
            "insights": "/api/shopping/insights",
            "feedback": "/api/shopping/feedback"
        }
    }

@app.post("/api/shopping/ai-predict")
async def generate_smart_shopping_list(request: ShoppingListRequest):
    """Generate intelligent shopping list using AI"""
    try:
        # Convert Pydantic models to dictionaries
        inventory_data = [item.dict() for item in request.current_inventory]
        history_data = [entry.dict() for entry in request.shopping_history]
        
        # Generate shopping list using AI service
        result = ai_shopping_service.generate_smart_shopping_list(
            user_id=request.user_id,
            current_inventory=inventory_data,
            shopping_history=history_data,
            budget_limit=request.budget_limit
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate shopping list: {str(e)}")

@app.post("/api/shopping/patterns")
async def analyze_shopping_patterns(request: PatternAnalysisRequest):
    """Analyze user shopping patterns"""
    try:
        history_data = [entry.dict() for entry in request.shopping_history]
        
        # Analyze patterns
        user_pattern = ai_shopping_service.pattern_analyzer.analyze_shopping_history(
            request.user_id, history_data
        )
        
        return {
            "success": True,
            "user_id": request.user_id,
            "patterns": {
                "item_frequencies": user_pattern.item_frequencies,
                "category_preferences": user_pattern.category_preferences,
                "seasonal_patterns": user_pattern.seasonal_patterns,
                "budget_patterns": user_pattern.budget_patterns
            },
            "analysis_date": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze patterns: {str(e)}")

@app.get("/api/shopping/insights/{user_id}")
async def get_shopping_insights(user_id: str):
    """Get shopping insights for a user"""
    try:
        insights = ai_shopping_service.get_shopping_insights(user_id)
        return {
            "success": True,
            "user_id": user_id,
            "insights": insights,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get insights: {str(e)}")

@app.post("/api/shopping/feedback")
async def submit_feedback(request: FeedbackRequest, background_tasks: BackgroundTasks):
    """Submit feedback to improve AI predictions"""
    try:
        # Process feedback in background
        background_tasks.add_task(
            ai_shopping_service.learn_from_feedback,
            request.user_id,
            request.item_name,
            request.feedback
        )
        
        return {
            "success": True,
            "message": "Feedback received and will be processed",
            "user_id": request.user_id,
            "item": request.item_name,
            "feedback": request.feedback
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process feedback: {str(e)}")

@app.post("/api/shopping/smart-prioritize")
async def smart_prioritize_list(shopping_list: List[Dict], user_id: str, budget_limit: Optional[float] = None):
    """Intelligently prioritize shopping list items"""
    try:
        # Convert to ShoppingItem objects
        from ai_shopping_service import ShoppingItem
        
        items = []
        for item_data in shopping_list:
            items.append(ShoppingItem(
                name=item_data.get('name', ''),
                category=item_data.get('category', 'other'),
                brand=item_data.get('brand'),
                price=item_data.get('price'),
                quantity=item_data.get('quantity', 1),
                unit=item_data.get('unit', 'piece'),
                confidence=item_data.get('confidence', 0.5),
                reason=item_data.get('reason', 'User added')
            ))
        
        # Get user pattern if available
        user_pattern = ai_shopping_service.pattern_analyzer.user_patterns.get(user_id)
        if not user_pattern:
            # Create basic pattern
            from ai_shopping_service import UserPattern
            user_pattern = UserPattern(
                user_id=user_id,
                item_frequencies={},
                category_preferences={'other': 1.0},
                seasonal_patterns={},
                time_patterns={},
                budget_patterns={}
            )
        
        # Prioritize items
        prioritized_items = ai_shopping_service.prioritization_service.prioritize_items(
            items, user_pattern, budget_limit
        )
        
        return {
            "success": True,
            "prioritized_list": [ai_shopping_service._item_to_dict(item) for item in prioritized_items],
            "total_items": len(prioritized_items),
            "budget_applied": budget_limit is not None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to prioritize list: {str(e)}")

@app.get("/api/shopping/categories")
async def get_categories():
    """Get available shopping categories"""
    return {
        "success": True,
        "categories": [
            "fruits",
            "vegetables", 
            "dairy",
            "meat",
            "grains",
            "snacks",
            "beverages",
            "household",
            "personal_care",
            "other"
        ]
    }

@app.get("/api/shopping/seasonal/{month}")
async def get_seasonal_recommendations(month: str):
    """Get seasonal shopping recommendations"""
    try:
        # Simple seasonal recommendations
        seasonal_items = {
            "january": ["citrus fruits", "winter vegetables", "hearty soups"],
            "april": ["spring vegetables", "fresh herbs", "light salads"],
            "july": ["summer fruits", "grilling items", "cold beverages"],
            "october": ["pumpkins", "apples", "warm spices"]
        }
        
        month_lower = month.lower()
        recommendations = seasonal_items.get(month_lower, [])
        
        return {
            "success": True,
            "month": month,
            "seasonal_recommendations": recommendations,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get seasonal recommendations: {str(e)}")

@app.get("/api/shopping/health-check")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AI Shopping List API",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# Development server
if __name__ == "__main__":
    print("🚀 Starting AI Shopping List API Server...")
    print("📝 API Documentation: http://localhost:8001/docs")
    print("🔍 Health Check: http://localhost:8001/api/shopping/health-check")
    
    uvicorn.run(
        "ai_shopping_api:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )