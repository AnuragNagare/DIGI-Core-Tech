"""
Direct test of HuggingFace classifier without API
"""

from huggingface_food_classifier import food_classifier
from PIL import Image
import io

print("=" * 70)
print("🧪 DIRECT TEST OF HUGGINGFACE CLASSIFIER")
print("=" * 70)

# Load the pizza image we downloaded
print("\n📸 Loading test_pizza.jpg...")
with open('test_pizza.jpg', 'rb') as f:
    img_bytes = f.read()

print("✅ Image loaded")

print("\n🔍 Classifying...")
result = food_classifier.classify_food(img_bytes)

print("\n" + "=" * 70)
print("📊 CLASSIFICATION RESULT:")
print("=" * 70)

print(f"\n🤖 Model: {result.get('model_name', 'unknown')}")
print(f"📊 Classes: {result.get('model_classes', '?')}")
print(f"🔬 Confidence: {result.get('confidence', 0) * 100:.1f}%")

if result.get('ingredients'):
    ing = result['ingredients'][0]
    print(f"\n✨ Detected: {ing['name']}")
    print(f"   Category: {ing.get('category', 'unknown')}")
    
    if 'nutritional_info' in ing:
        nut = ing['nutritional_info']
        print(f"\n📊 Nutrition:")
        print(f"   Calories: {nut.get('calories', 0)} kcal")
        print(f"   Protein: {nut.get('protein', 0)}g")
        print(f"   Carbs: {nut.get('carbohydrates', 0)}g")
        print(f"   Fat: {nut.get('fat', 0)}g")

print("\n" + "=" * 70)

if result.get('model_name') and 'HuggingFace' in result.get('model_name', ''):
    print("✅ SUCCESS: Using HuggingFace Vision Transformer!")
else:
    print("❌ FAIL: Not using HuggingFace model")

print("=" * 70)
