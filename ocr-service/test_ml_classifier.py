"""
Test the ML-based food classifier with a real banana image
"""

import requests
from PIL import Image
import io
import sys

def test_ml_classifier():
    """Test ML classifier with banana image."""
    
    print("=" * 60)
    print("🧪 Testing ML-Based Food Classifier")
    print("=" * 60)
    
    # Create test banana image
    print("\n📸 Creating test banana image...")
    img = Image.new('RGB', (224, 224), (240, 220, 50))  # Bright yellow banana
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes = img_bytes.getvalue()
    
    print("✅ Test image created")
    
    # Test the API
    url = "http://127.0.0.1:8001/classify-food"
    
    print(f"\n🌐 Sending request to {url}...")
    
    try:
        files = {'file': ('banana.png', img_bytes, 'image/png')}
        response = requests.post(url, files=files, timeout=30)
        
        print(f"📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print("\n" + "=" * 60)
            print("✅ SUCCESS - Classification Result:")
            print("=" * 60)
            
            print(f"\n🎯 Model Type: {result.get('model_type', 'unknown')}")
            print(f"🤖 Model Name: {result.get('model_name', 'unknown')}")
            print(f"🔬 Confidence: {result.get('confidence', 0) * 100:.1f}%")
            
            if result.get('ingredients'):
                print(f"\n🥗 Detected Ingredient:")
                for ing in result['ingredients']:
                    print(f"  • {ing['name']} ({ing['confidence']*100:.1f}% confident)")
                    print(f"    Category: {ing.get('category', 'unknown')}")
                    if 'nutritional_info' in ing:
                        nut = ing['nutritional_info']
                        print(f"    Calories: {nut.get('calories', 0)} kcal")
                        print(f"    Protein: {nut.get('protein', 0)}g")
                        print(f"    Carbs: {nut.get('carbohydrates', 0)}g")
            
            if 'calorie_analysis' in result:
                cal = result['calorie_analysis']
                print(f"\n📊 Nutrition Analysis:")
                print(f"  Total Calories: {cal.get('total_calories', 0)} kcal")
                print(f"  Protein: {cal.get('total_protein', 0)}g")
                print(f"  Carbs: {cal.get('total_carbs', 0)}g")
                print(f"  Fat: {cal.get('total_fat', 0)}g")
                print(f"  Fiber: {cal.get('total_fiber', 0)}g")
                
                if 'nutritional_quality' in cal:
                    qual = cal['nutritional_quality']
                    print(f"\n⭐ Quality Score: {qual.get('quality_score', 0):.1f}/100")
                    print(f"  Rating: {qual.get('quality_rating', 'unknown')}")
            
            print("\n" + "=" * 60)
            
            # Check if using ML or fallback
            if result.get('model_type') == 'deep_learning':
                print("✅ USING ML-BASED CLASSIFIER (TensorFlow/Keras)")
            else:
                print("⚠️ USING FALLBACK CLASSIFIER (color-based)")
            
            print("=" * 60)
            
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("\n❌ Connection Error!")
        print("Make sure the food service is running on port 8001:")
        print("  cd ocr-service")
        print("  python -m uvicorn food_service:app --host 0.0.0.0 --port 8001 --reload")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    test_ml_classifier()
