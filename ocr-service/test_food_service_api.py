import requests
from PIL import Image
import io
import base64

# Create a banana-colored test image
print("Creating banana test image...")
img = Image.new('RGB', (400, 300), color=(240, 220, 80))  # Yellow/banana color
buf = io.BytesIO()
img.save(buf, format='JPEG', quality=95)
buf.seek(0)

# Upload to food classification service
url = "http://127.0.0.1:8001/classify-food"
files = {'file': ('banana.jpg', buf, 'image/jpeg')}

print("Uploading to food classification service...")
response = requests.post(url, files=files, timeout=30)

print(f"\nResponse Status: {response.status_code}")
if response.status_code == 200:
    result = response.json()
    
    print("\n" + "="*60)
    print("FOOD SERVICE TEST RESULT")
    print("="*60)
    print(f"Success: {result.get('success')}")
    print(f"Confidence: {result.get('confidence', 0):.2%}")
    print(f"Total Ingredients: {result.get('total_ingredients', 0)}")
    
    if result.get('ingredients'):
        for i, ing in enumerate(result['ingredients'], 1):
            print(f"\n{i}. {ing.get('name', 'Unknown')}")
            print(f"   Confidence: {ing.get('confidence', 0):.2%}")
            print(f"   Category: {ing.get('category', 'N/A')}")
            
            if 'nutritional_info' in ing:
                nutr = ing['nutritional_info']
                print(f"   Calories: {nutr.get('calories', 'N/A')} kcal")
                print(f"   Protein: {nutr.get('protein', 'N/A')}g")
                print(f"   Carbs: {nutr.get('carbohydrates', 'N/A')}g")
                print(f"   Fat: {nutr.get('fat', 'N/A')}g")
                
            if 'key_nutrients' in ing:
                print(f"   Key Nutrients: {', '.join(ing.get('key_nutrients', []))}")
        
        # Check if banana was detected
        top_name = result['ingredients'][0].get('name', '').lower()
        if 'banana' in top_name:
            print("\n✅ SUCCESS: Food service correctly identified as BANANA!")
            print("🎉 The food classification feature is working!")
        else:
            print(f"\n⚠️  Top prediction: {top_name}")
    
    print("="*60)
else:
    print(f"Error: {response.text}")
