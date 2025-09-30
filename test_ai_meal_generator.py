#!/usr/bin/env python3
"""
Test script for AI Meal Generator
Tests 5 different scenarios with sample inventory items
"""

import json
import requests
from typing import List, Dict

def test_ai_meal_generation():
    """Test AI meal generation with 5 different scenarios"""
    
    base_url = "http://localhost:8003"
    
    # Test scenarios
    test_scenarios = [
        {
            "name": "Scenario 1: Basic Breakfast Items",
            "ingredients": [
                {"name": "Bananas", "quantity": 6, "unit": "pieces", "expires_in_days": 3},
                {"name": "Milk", "quantity": 1, "unit": "liter", "expires_in_days": 6},
                {"name": "Eggs", "quantity": 12, "unit": "pieces", "expires_in_days": 8},
            ],
            "preferences": {
                "dietary_restrictions": [],
                "max_cooking_time": 30,
                "servings": 2,
                "meal_type": "breakfast"
            }
        },
        {
            "name": "Scenario 2: Protein & Vegetable Dinner",
            "ingredients": [
                {"name": "Chicken Breast", "quantity": 500, "unit": "g", "expires_in_days": 4},
                {"name": "Bell Peppers", "quantity": 2, "unit": "pieces", "expires_in_days": 7},
                {"name": "Onions", "quantity": 3, "unit": "pieces", "expires_in_days": 13},
                {"name": "Tomatoes", "quantity": 4, "unit": "pieces", "expires_in_days": 5},
            ],
            "preferences": {
                "dietary_restrictions": [],
                "max_cooking_time": 45,
                "servings": 4,
                "meal_type": "dinner"
            }
        },
        {
            "name": "Scenario 3: Carb-Based Lunch",
            "ingredients": [
                {"name": "Pasta", "quantity": 500, "unit": "g", "expires_in_days": 350},
                {"name": "Tomatoes", "quantity": 4, "unit": "pieces", "expires_in_days": 5},
                {"name": "Onions", "quantity": 3, "unit": "pieces", "expires_in_days": 13},
            ],
            "preferences": {
                "dietary_restrictions": ["vegetarian"],
                "max_cooking_time": 25,
                "servings": 3,
                "meal_type": "lunch"
            }
        },
        {
            "name": "Scenario 4: Dairy & Grain Combination",
            "ingredients": [
                {"name": "Greek Yogurt", "quantity": 500, "unit": "g", "expires_in_days": 2},
                {"name": "Rice", "quantity": 2, "unit": "cups", "expires_in_days": 365},
                {"name": "Milk", "quantity": 1, "unit": "liter", "expires_in_days": 6},
            ],
            "preferences": {
                "dietary_restrictions": [],
                "max_cooking_time": 20,
                "servings": 2,
                "meal_type": "snack"
            }
        },
        {
            "name": "Scenario 5: Mixed Ingredients Challenge",
            "ingredients": [
                {"name": "Eggs", "quantity": 12, "unit": "pieces", "expires_in_days": 8},
                {"name": "Bell Peppers", "quantity": 2, "unit": "pieces", "expires_in_days": 7},
                {"name": "Rice", "quantity": 2, "unit": "cups", "expires_in_days": 365},
                {"name": "Greek Yogurt", "quantity": 500, "unit": "g", "expires_in_days": 2},
                {"name": "Bananas", "quantity": 6, "unit": "pieces", "expires_in_days": 3},
            ],
            "preferences": {
                "dietary_restrictions": [],
                "max_cooking_time": 35,
                "servings": 3,
                "meal_type": "dinner"
            }
        }
    ]
    
    print("🧪 Starting AI Meal Generator Tests...")
    print("=" * 60)
    
    successful_tests = 0
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n🔍 {scenario['name']}")
        print("-" * 40)
        
        # Prepare request payload
        payload = {
            "user_id": f"test_user_{i}",
            "available_ingredients": scenario["ingredients"],
            **scenario["preferences"]
        }
        
        try:
            # Make API request
            response = requests.post(
                f"{base_url}/generate-meals",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                meals = data.get("meals", [])
                
                print(f"✅ SUCCESS: Generated {len(meals)} meal(s)")
                
                for j, meal in enumerate(meals[:2], 1):  # Show first 2 meals
                    print(f"   {j}. {meal.get('name', 'Unknown Meal')}")
                    print(f"      - Cooking Time: {meal.get('estimated_prep_time', 'N/A')} min")
                    print(f"      - Ingredients: {len(meal.get('ingredients', []))} items")
                    print(f"      - Instructions: {len(meal.get('instructions', []))} steps")
                
                successful_tests += 1
                
            else:
                print(f"❌ FAILED: HTTP {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                
        except requests.exceptions.ConnectionError:
            print("❌ FAILED: Could not connect to AI Meal Service (http://localhost:8003)")
            print("   Make sure the service is running!")
            
        except requests.exceptions.Timeout:
            print("❌ FAILED: Request timed out")
            
        except Exception as e:
            print(f"❌ FAILED: {str(e)}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {successful_tests}/{len(test_scenarios)} scenarios successful")
    
    if successful_tests == len(test_scenarios):
        print("🎉 ALL TESTS PASSED! AI Meal Generator is working correctly!")
    elif successful_tests > 0:
        print(f"⚠️  PARTIAL SUCCESS: {successful_tests} out of {len(test_scenarios)} tests passed")
    else:
        print("❌ ALL TESTS FAILED. Please check the AI Meal Service.")
    
    return successful_tests == len(test_scenarios)

if __name__ == "__main__":
    test_ai_meal_generation()