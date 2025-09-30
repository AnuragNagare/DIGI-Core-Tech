#!/usr/bin/env python3

import requests
import json
import sys

# Test scenarios
test_scenarios = [
    {
        "name": "Test 1: Basic meal generation with common ingredients",
        "data": {
            "user_id": "test_user_1",
            "available_ingredients": ["bananas", "milk", "eggs"],
            "dietary_restrictions": [],
            "max_cooking_time": 30,
            "servings": 2
        }
    },
    {
        "name": "Test 2: Vegetarian meal with vegetables and grains",
        "data": {
            "user_id": "test_user_2", 
            "available_ingredients": ["chicken", "broccoli", "rice", "onions"],
            "dietary_restrictions": ["vegetarian"],
            "max_cooking_time": 45,
            "servings": 4
        }
    },
    {
        "name": "Test 3: Quick meal with limited cooking time",
        "data": {
            "user_id": "test_user_3",
            "available_ingredients": ["yogurt", "berries", "oats", "honey"],
            "dietary_restrictions": [],
            "max_cooking_time": 10,
            "servings": 1
        }
    },
    {
        "name": "Test 4: Protein-rich meal for fitness",
        "data": {
            "user_id": "test_user_4",
            "available_ingredients": ["chicken", "sweet_potato", "spinach", "olive_oil"],
            "dietary_restrictions": [],
            "max_cooking_time": 60,
            "servings": 2
        }
    },
    {
        "name": "Test 5: Family meal with multiple servings",
        "data": {
            "user_id": "test_user_5",
            "available_ingredients": ["pasta", "tomatoes", "cheese", "basil", "garlic"],
            "dietary_restrictions": [],
            "max_cooking_time": 40,
            "servings": 6
        }
    }
]

def test_ai_meal_generation():
    """Test AI meal generation with 5 different scenarios"""
    base_url = "http://localhost:8003"
    
    print("🤖 Testing AI Meal Generator - 5 Scenarios")
    print("=" * 50)
    
    results = []
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{scenario['name']}")
        print("-" * 40)
        
        try:
            # Test meal generation
            response = requests.post(
                f"{base_url}/generate-meals",
                json=scenario['data'],
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    meals = data.get('meals', [])
                    print(f"✅ SUCCESS: Generated {len(meals)} meals")
                    
                    for j, meal in enumerate(meals[:2], 1):  # Show first 2 meals
                        print(f"   📋 Meal {j}: {meal.get('name', 'Unknown')}")
                        print(f"      ⏱️ Prep: {meal.get('estimated_prep_time', 'N/A')} min")
                        print(f"      🍽️ Servings: {meal.get('servings', 'N/A')}")
                        print(f"      🏆 Confidence: {meal.get('confidence_score', 0)*100:.1f}%")
                    
                    results.append({
                        'scenario': i,
                        'status': 'success',
                        'meal_count': len(meals),
                        'names': [m.get('name') for m in meals[:3]]
                    })
                else:
                    print(f"❌ FAILED: {data.get('error', 'Unknown error')}")
                    results.append({
                        'scenario': i,
                        'status': 'failed',
                        'error': data.get('error')
                    })
            else:
                print(f"❌ HTTP ERROR: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                results.append({
                    'scenario': i,
                    'status': 'http_error',
                    'status_code': response.status_code
                })
                
        except requests.RequestException as e:
            print(f"❌ CONNECTION ERROR: {str(e)}")
            results.append({
                'scenario': i,
                'status': 'connection_error',
                'error': str(e)
            })
        except Exception as e:
            print(f"❌ UNEXPECTED ERROR: {str(e)}")
            results.append({
                'scenario': i,
                'status': 'unexpected_error',
                'error': str(e)
            })
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    successful = sum(1 for r in results if r['status'] == 'success')
    print(f"✅ Successful tests: {successful}/5")
    print(f"❌ Failed tests: {5-successful}/5")
    
    for result in results:
        status_emoji = "✅" if result['status'] == 'success' else "❌"
        print(f"{status_emoji} Test {result['scenario']}: {result['status']}")
        if result['status'] == 'success' and 'names' in result:
            print(f"   Generated: {', '.join(result['names'])}")
    
    if successful >= 3:
        print("\n🎉 AI Meal Generator is working well! Most tests passed.")
    else:
        print("\n⚠️ AI Meal Generator needs attention - multiple test failures.")
    
    return results

if __name__ == "__main__":
    test_ai_meal_generation()