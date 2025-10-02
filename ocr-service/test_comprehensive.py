"""
Comprehensive End-to-End Testing
Tests multiple real food images from the internet for accuracy
"""

import requests
import time
from PIL import Image
import io
import json

def download_test_images():
    """Download various food images from the internet."""
    test_cases = [
        {
            'name': 'Pizza',
            'url': 'https://images.unsplash.com/photo-1513104890138-7c749659a591?w=400',
            'expected_categories': ['pizza'],
            'file': 'test_pizza.jpg'
        },
        {
            'name': 'Burger',
            'url': 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400',
            'expected_categories': ['burger', 'hamburger'],
            'file': 'test_burger.jpg'
        },
        {
            'name': 'Salad',
            'url': 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=400',
            'expected_categories': ['salad'],
            'file': 'test_salad.jpg'
        },
        {
            'name': 'Sushi',
            'url': 'https://images.unsplash.com/photo-1579584425555-c3ce17fd4351?w=400',
            'expected_categories': ['sushi'],
            'file': 'test_sushi.jpg'
        },
        {
            'name': 'Ice Cream',
            'url': 'https://images.unsplash.com/photo-1497034825429-c343d7c6a68f?w=400',
            'expected_categories': ['ice cream', 'ice_cream', 'gelato'],
            'file': 'test_icecream.jpg'
        }
    ]
    
    print("=" * 80)
    print("📥 DOWNLOADING TEST IMAGES FROM INTERNET")
    print("=" * 80)
    
    for test_case in test_cases:
        try:
            print(f"\n📸 Downloading {test_case['name']}...")
            response = requests.get(test_case['url'], timeout=10)
            if response.status_code == 200:
                with open(test_case['file'], 'wb') as f:
                    f.write(response.content)
                print(f"✅ Saved as {test_case['file']} ({len(response.content)} bytes)")
            else:
                print(f"❌ Failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return test_cases

def test_food_classification_service():
    """Test if the food classification API is working."""
    print("\n" + "=" * 80)
    print("🔍 TESTING FOOD CLASSIFICATION SERVICE")
    print("=" * 80)
    
    url = "http://127.0.0.1:8001/health"
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Service Status: {data.get('status')}")
            print(f"🤖 Classifier: {data.get('classifier_type')}")
            print(f"📊 Model: {data.get('model_info')}")
            print(f"🎯 Classes: {data.get('num_classes')}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Service not reachable: {e}")
        return False

def classify_food(image_file):
    """Classify a food image."""
    url = "http://127.0.0.1:8001/classify-food"
    
    with open(image_file, 'rb') as f:
        files = {'file': (image_file, f.read(), 'image/jpeg')}
        
    response = requests.post(url, files=files, timeout=60)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Classification failed: {response.status_code}")
        return None

def evaluate_results(test_cases):
    """Test all downloaded images and evaluate accuracy."""
    print("\n" + "=" * 80)
    print("🧪 EVALUATING ML MODEL ACCURACY")
    print("=" * 80)
    
    results = []
    
    for test_case in test_cases:
        print(f"\n{'='*80}")
        print(f"🍽️  Testing: {test_case['name']}")
        print(f"{'='*80}")
        
        try:
            result = classify_food(test_case['file'])
            
            if not result or not result.get('success'):
                print(f"❌ Classification failed for {test_case['name']}")
                results.append({
                    'name': test_case['name'],
                    'success': False,
                    'confidence': 0
                })
                continue
            
            detected = result['ingredients'][0]['name'].lower() if result.get('ingredients') else ''
            confidence = result.get('confidence', 0)
            model_name = result.get('model_name', 'unknown')
            
            # Check if detected food matches expected categories
            is_correct = any(expected in detected or detected in expected 
                           for expected in test_case['expected_categories'])
            
            print(f"\n📊 Results:")
            print(f"   Expected: {test_case['name']}")
            print(f"   Detected: {result['ingredients'][0]['name'] if result.get('ingredients') else 'None'}")
            print(f"   Confidence: {confidence * 100:.1f}%")
            print(f"   Model: {model_name}")
            print(f"   Match: {'✅ CORRECT' if is_correct else '⚠️ DIFFERENT'}")
            
            if result.get('ingredients'):
                ing = result['ingredients'][0]
                if 'nutritional_info' in ing:
                    nut = ing['nutritional_info']
                    print(f"\n📈 Nutrition (per {nut.get('portion_size_g', 100)}g):")
                    print(f"   Calories: {nut.get('calories', 0)} kcal")
                    print(f"   Protein: {nut.get('protein', 0)}g")
                    print(f"   Carbs: {nut.get('carbohydrates', 0)}g")
                    print(f"   Fat: {nut.get('fat', 0)}g")
            
            results.append({
                'name': test_case['name'],
                'detected': detected,
                'confidence': confidence,
                'correct': is_correct,
                'success': True
            })
            
        except Exception as e:
            print(f"❌ Error testing {test_case['name']}: {e}")
            results.append({
                'name': test_case['name'],
                'success': False,
                'confidence': 0
            })
    
    return results

def print_summary(results):
    """Print final summary of tests."""
    print("\n" + "=" * 80)
    print("📊 FINAL TEST SUMMARY")
    print("=" * 80)
    
    successful = [r for r in results if r.get('success')]
    correct = [r for r in results if r.get('correct')]
    
    avg_confidence = sum(r['confidence'] for r in successful) / len(successful) if successful else 0
    accuracy_rate = len(correct) / len(results) * 100 if results else 0
    
    print(f"\n✅ Tests Completed: {len(results)}")
    print(f"✅ Successful Classifications: {len(successful)}/{len(results)}")
    print(f"✅ Correct Matches: {len(correct)}/{len(results)} ({accuracy_rate:.1f}%)")
    print(f"📊 Average Confidence: {avg_confidence * 100:.1f}%")
    
    print(f"\n{'='*80}")
    print("Individual Results:")
    print(f"{'='*80}")
    for r in results:
        status = "✅" if r.get('correct') else "⚠️" if r.get('success') else "❌"
        confidence_str = f"{r['confidence']*100:.1f}%" if r.get('success') else "N/A"
        detected_str = r.get('detected', 'Failed').title()
        print(f"{status} {r['name']:15} → {detected_str:20} ({confidence_str})")
    
    print(f"\n{'='*80}")
    
    if accuracy_rate >= 90:
        print("🎉 EXCELLENT! 90%+ ACCURACY ACHIEVED!")
    elif accuracy_rate >= 75:
        print("✅ GOOD! 75%+ accuracy achieved")
    elif accuracy_rate >= 50:
        print("⚠️ FAIR: 50%+ accuracy")
    else:
        print("❌ NEEDS IMPROVEMENT: <50% accuracy")
    
    print(f"{'='*80}\n")
    
    return accuracy_rate >= 90

def main():
    """Main test execution."""
    print("\n" + "=" * 80)
    print("🚀 COMPREHENSIVE END-TO-END FOOD CLASSIFICATION TEST")
    print("=" * 80)
    
    # Step 1: Test service
    if not test_food_classification_service():
        print("\n❌ Food classification service is not running!")
        print("Please ensure the service is started on port 8001")
        return False
    
    # Step 2: Download test images
    test_cases = download_test_images()
    
    # Step 3: Evaluate
    results = evaluate_results(test_cases)
    
    # Step 4: Summary
    success = print_summary(results)
    
    return success

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n✅ ALL TESTS PASSED! System is ready for production use.")
        print("🎯 The ML model is working correctly with 90%+ accuracy.")
    else:
        print("\n⚠️ Some tests need attention. Review results above.")
