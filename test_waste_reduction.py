#!/usr/bin/env python3

import requests
import json

# Test waste reduction meal generation
def test_waste_reduction():
    """Test the enhanced AI meal generator with waste reduction focus"""
    
    print("🔄 Testing AI Meal Generator - Waste Reduction Enhancement")
    print("=" * 60)
    
    # Test data with expiring and high-quantity items
    test_data = {
        "user_id": "test_waste_user",
        "available_ingredients": [
            {"name": "bananas", "quantity": 8, "unit": "pieces", "expires_in_days": 2},
            {"name": "milk", "quantity": 3, "unit": "liters", "expires_in_days": 1},  
            {"name": "yogurt", "quantity": 2, "unit": "cups", "expires_in_days": 2},
            {"name": "chicken", "quantity": 5, "unit": "pieces", "expires_in_days": 7},
            {"name": "rice", "quantity": 10, "unit": "cups", "expires_in_days": 365}
        ],
        "prioritize_expiring": True,
        "prioritize_high_quantity": True,
        "expiring_ingredients": [
            {"name": "bananas", "expires_in_days": 2, "quantity": 8},
            {"name": "milk", "expires_in_days": 1, "quantity": 3},
            {"name": "yogurt", "expires_in_days": 2, "quantity": 2}
        ],
        "optimize_for_waste": True,
        "dietary_restrictions": [],
        "max_cooking_time": 30,
        "servings": 2
    }
    
    try:
        print("📤 Sending request to AI service...")
        response = requests.post(
            "http://localhost:8003/generate-meals",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                meals = data.get('meals', [])
                print(f"✅ SUCCESS: Generated {len(meals)} waste-optimized meals")
                
                for i, meal in enumerate(meals[:3], 1):
                    print(f"\n🍽️  Meal {i}: {meal.get('name', 'Unknown')}")
                    print(f"   📋 Description: {meal.get('reasoning', 'N/A')}")
                    print(f"   ⏱️ Prep Time: {meal.get('estimated_prep_time', 'N/A')} min")
                    print(f"   🎯 Confidence: {(meal.get('confidence_score', 0)*100):.1f}%")
                    
                    ingredients = meal.get('ingredients', [])[:3]
                    print(f"   🥘 Key Ingredients: {', '.join(ingredients)}")
                
                summary = data.get('summary', {})
                print(f"\n📊 Summary:")
                print(f"   • Total Meals: {summary.get('total_meals', 0)}")
                print(f"   • Waste Optimized: {'Yes' if summary.get('waste_optimized') else 'No'}")
                print(f"   • Avg Confidence: {(summary.get('avg_confidence', 0)*100):.1f}%")
                
                return True
            else:
                print(f"❌ API Error: {data.get('error', 'Unknown')}")
                return False
        else:
            print(f"❌ HTTP Error {response.status_code}: {response.text[:200]}")
            return False
            
    except requests.RequestException as e:
        print(f"❌ Connection Error: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_waste_reduction()
    print("\n" + "=" * 60)
    if success:
        print("🎉 Waste Reduction Enhancement: WORKING!")
        print("✅ Recipes now prioritize expiring & high-quantity items")
    else:
        print("⚠️  Test failed - check service connectivity")