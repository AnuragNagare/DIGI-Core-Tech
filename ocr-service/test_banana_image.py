import sys
import os
import requests
from io import BytesIO
from PIL import Image

# Add current directory to path
sys.path.insert(0, '.')

print("Loading food classification service...")
from food_classification_service import food_classifier

print("\nFood classifier loaded successfully!")
print(f"Model device: {food_classifier.device}")
print(f"Number of food categories: {len(food_classifier.food_prompts_cache)}")

# Download the banana image from the user
print("\nDownloading banana image...")
banana_url = "https://github.com/user-attachments/assets/8d7e2aef-fb7e-4e7a-9c75-4d7c3e6e6a9e"

try:
    response = requests.get(banana_url, timeout=10)
    if response.status_code == 200:
        image_bytes = response.content
        
        # Verify it's a valid image
        img = Image.open(BytesIO(image_bytes))
        print(f"Image loaded: {img.format} {img.size} {img.mode}")
        
        print("\nClassifying banana image...")
        result = food_classifier.classify_food(image_bytes)
        
        print("\n" + "="*60)
        print("CLASSIFICATION RESULT:")
        print("="*60)
        print(f"Success: {result.get('success')}")
        print(f"Confidence: {result.get('confidence', 0):.2%}")
        
        if result.get('ingredients'):
            print(f"\nDetected Ingredients ({len(result['ingredients'])}):")
            for i, ingredient in enumerate(result['ingredients'], 1):
                print(f"\n{i}. {ingredient.get('name', 'Unknown').upper()}")
                print(f"   Confidence: {ingredient.get('confidence', 0):.2%}")
                print(f"   Category: {ingredient.get('category', 'N/A')}")
                
                # Nutritional info
                if 'nutritional_info' in ingredient:
                    nutr = ingredient['nutritional_info']
                    print(f"   Calories: {nutr.get('calories', 'N/A')} kcal")
                    print(f"   Protein: {nutr.get('protein', 'N/A')}g")
                    print(f"   Carbs: {nutr.get('carbohydrates', 'N/A')}g")
                    print(f"   Fat: {nutr.get('fat', 'N/A')}g")
                    print(f"   Fiber: {nutr.get('fiber', 'N/A')}g")
                    
                if 'key_nutrients' in ingredient:
                    print(f"   Key Nutrients: {', '.join(ingredient['key_nutrients'])}")
        
        print("\n" + "="*60)
        
        # Check if it correctly identified as banana
        if result.get('ingredients'):
            top_prediction = result['ingredients'][0]['name'].lower()
            if 'banana' in top_prediction:
                print("✅ SUCCESS: Correctly identified as BANANA!")
            else:
                print(f"❌ FAILED: Identified as '{top_prediction}' instead of banana")
                print("\nTop 5 predictions for debugging:")
                for i, ing in enumerate(result['ingredients'][:5], 1):
                    print(f"{i}. {ing['name']} ({ing['confidence']:.2%})")
        
    else:
        print(f"Failed to download image: HTTP {response.status_code}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
