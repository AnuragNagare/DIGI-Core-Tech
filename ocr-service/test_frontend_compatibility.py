import requests
from PIL import Image
import io
import json

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
    print("FRONTEND COMPATIBILITY TEST")
    print("="*60)
    
    # Check all required fields
    checks = {
        'success': result.get('success'),
        'ingredients (array)': isinstance(result.get('ingredients'), list),
        'confidence': 'confidence' in result,
        'total_ingredients': 'total_ingredients' in result,
        'calorie_analysis': 'calorie_analysis' in result,
        'calorie_analysis.detailed_breakdown': isinstance(result.get('calorie_analysis', {}).get('detailed_breakdown'), list),
        'detailed_breakdown length > 0': len(result.get('calorie_analysis', {}).get('detailed_breakdown', [])) > 0,
        'nutritional_analysis': 'nutritional_analysis' in result,
        'meal_suggestions': 'meal_suggestions' in result,
        'dietary_labels': 'dietary_labels' in result
    }
    
    print("\nField Checks:")
    all_passed = True
    for check_name, check_result in checks.items():
        status = "✅" if check_result else "❌"
        print(f"  {status} {check_name}: {check_result}")
        if not check_result:
            all_passed = False
    
    if all_passed:
        print("\n✅ ALL CHECKS PASSED - Frontend compatibility verified!")
    else:
        print("\n❌ SOME CHECKS FAILED - Fix required")
    
    # Show calorie analysis structure
    if result.get('calorie_analysis'):
        ca = result['calorie_analysis']
        print("\n" + "-"*60)
        print("Calorie Analysis Structure:")
        print(f"  Total Calories: {ca.get('total_calories')} kcal")
        print(f"  Total Protein: {ca.get('total_protein')}g")
        print(f"  Total Carbs: {ca.get('total_carbs')}g")
        print(f"  Total Fat: {ca.get('total_fat')}g")
        print(f"  Total Fiber: {ca.get('total_fiber')}g")
        print(f"  Total Weight: {ca.get('total_weight_g')}g")
        print(f"  Calories per 100g: {ca.get('calories_per_100g'):.1f}")
        print(f"  Meal Type: {ca.get('meal_type')}")
        
        if ca.get('detailed_breakdown'):
            print(f"\n  Detailed Breakdown ({len(ca['detailed_breakdown'])} items):")
            for item in ca['detailed_breakdown']:
                print(f"    - {item.get('name')}: {item.get('calories')} kcal, {item.get('portion_size_g')}g")
        
        if ca.get('nutritional_quality'):
            nq = ca['nutritional_quality']
            print(f"\n  Nutritional Quality:")
            print(f"    Score: {nq.get('quality_score'):.1f}")
            print(f"    Rating: {nq.get('quality_rating')}")
            print(f"    Protein %: {nq.get('protein_percentage'):.1f}%")
            print(f"    Fat %: {nq.get('fat_percentage'):.1f}%")
    
    print("\n" + "="*60)
    print("SAMPLE RESPONSE (for debugging):")
    print(json.dumps(result, indent=2)[:1000] + "...")
    print("="*60)
    
else:
    print(f"Error: {response.text}")
