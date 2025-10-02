from lightweight_food_classifier import food_classifier
from PIL import Image
import io

# Create a test yellow/banana-colored image
print("Creating test banana-colored image...")
img = Image.new('RGB', (300, 200), color=(240, 220, 80))  # Yellow/banana color
buf = io.BytesIO()
img.save(buf, format='PNG')
image_bytes = buf.getvalue()

print(f"Image size: {len(image_bytes)} bytes")

print("\nClassifying...")
result = food_classifier.classify_food(image_bytes)

print("\n" + "="*60)
print("BANANA-COLORED IMAGE CLASSIFICATION TEST")
print("="*60)
print(f"Success: {result['success']}")
print(f"Confidence: {result.get('confidence', 0):.2%}")

if result['ingredients']:
    top = result['ingredients'][0]
    print(f"\nTop Match: {top['name']}")
    print(f"Category: {top['category']}")
    print(f"\nNutritional Info (per {top['nutritional_info']['portion_description']}):")
    print(f"  Calories: {top['nutritional_info']['calories']} kcal")
    print(f"  Protein: {top['nutritional_info']['protein']}g")
    print(f"  Carbohydrates: {top['nutritional_info']['carbohydrates']}g")
    print(f"  Fat: {top['nutritional_info']['fat']}g")
    print(f"  Fiber: {top['nutritional_info']['fiber']}g")
    print(f"  Key Nutrients: {', '.join(top['key_nutrients'])}")
    
    if 'banana' in top['name'].lower():
        print("\n✅ SUCCESS: Correctly identified as BANANA!")
    else:
        print(f"\n⚠️  Top match: '{top['name']}' (not banana)")
        print("\nAll matches:")
        for i, ing in enumerate(result['ingredients'], 1):
            print(f"  {i}. {ing['name']} ({ing['confidence']:.2%})")
else:
    print("No matches found")

print("\nColor Analysis:")
if 'color_analysis' in result:
    ca = result['color_analysis']
    print(f"  Hue: {ca['hue']:.1f}°")
    print(f"  Saturation: {ca['saturation']:.1f}")
    print(f"  Lightness: {ca['lightness']:.1f}")
    print(f"  RGB: {tuple(int(x) for x in ca['rgb'])}")

print("="*60)
