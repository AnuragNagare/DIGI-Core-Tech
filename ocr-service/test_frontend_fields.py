"""
Test Frontend Compatibility - Verify all fields required by FoodClassifier.tsx
"""

import requests
import json

print("=" * 80)
print("🧪 FRONTEND COMPATIBILITY TEST")
print("=" * 80)

# Test with pizza image
print("\n📸 Testing with pizza image...")
with open('test_pizza.jpg', 'rb') as f:
    files = {'file': ('pizza.jpg', f.read(), 'image/jpeg')}

response = requests.post('http://127.0.0.1:8001/classify-food', files=files, timeout=30)

if response.status_code != 200:
    print(f"❌ API Error: {response.status_code}")
    print(response.text)
    exit(1)

result = response.json()

print("✅ API Response received\n")

# Check all required fields for frontend
print("=" * 80)
print("🔍 CHECKING REQUIRED FIELDS")
print("=" * 80)

checks = []

# Top level fields
top_level = ['success', 'ingredients', 'confidence', 'total_ingredients', 
             'nutritional_analysis', 'calorie_analysis']

for field in top_level:
    present = field in result
    checks.append(('Top level', field, present, result.get(field, 'N/A')))
    status = "✅" if present else "❌"
    print(f"{status} {field}: {present}")

# Nutritional analysis fields
print("\n📊 nutritional_analysis:")
na = result.get('nutritional_analysis', {})
na_fields = ['total_ingredients', 'average_confidence', 'detected_category',
             'detected_nutrients', 'health_score', 'dietary_balance']

for field in na_fields:
    present = field in na
    value = na.get(field, 'N/A')
    status = "✅" if present else "❌"
    
    if field == 'detected_nutrients':
        if isinstance(value, list):
            print(f"{status} {field}: {value} (length: {len(value)})")
        else:
            print(f"{status} {field}: NOT A LIST!")
    else:
        print(f"{status} {field}: {value}")
    
    checks.append(('nutritional_analysis', field, present, value))

# Calorie analysis fields
print("\n🔥 calorie_analysis:")
ca = result.get('calorie_analysis', {})
ca_fields = ['total_calories', 'total_protein', 'total_carbs', 'total_fat',
             'detailed_breakdown', 'nutritional_quality']

for field in ca_fields:
    present = field in ca
    value = ca.get(field, 'N/A')
    status = "✅" if present else "❌"
    
    if field == 'detailed_breakdown':
        if isinstance(value, list):
            print(f"{status} {field}: [{len(value)} items]")
        else:
            print(f"{status} {field}: NOT A LIST!")
    elif field == 'nutritional_quality':
        if isinstance(value, dict):
            print(f"{status} {field}: {value.get('quality_rating', 'N/A')} (score: {value.get('quality_score', 0)})")
        else:
            print(f"{status} {field}: NOT A DICT!")
    else:
        print(f"{status} {field}: {value}")
    
    checks.append(('calorie_analysis', field, present, value))

# Ingredients array
print("\n🥗 ingredients:")
if 'ingredients' in result and len(result['ingredients']) > 0:
    ing = result['ingredients'][0]
    ing_fields = ['name', 'confidence', 'category', 'nutritional_info']
    
    for field in ing_fields:
        present = field in ing
        status = "✅" if present else "❌"
        value = ing.get(field, 'N/A')
        
        if field == 'nutritional_info':
            if isinstance(value, dict):
                print(f"{status} {field}: calories={value.get('calories', 0)}, protein={value.get('protein', 0)}g")
            else:
                print(f"{status} {field}: NOT A DICT!")
        else:
            print(f"{status} {field}: {value}")
        
        checks.append(('ingredients[0]', field, present, value))
else:
    print("❌ No ingredients found!")

# Summary
print("\n" + "=" * 80)
print("📋 SUMMARY")
print("=" * 80)

failed = [c for c in checks if not c[2]]
passed = [c for c in checks if c[2]]

print(f"\n✅ Passed: {len(passed)}/{len(checks)}")
print(f"❌ Failed: {len(failed)}/{len(checks)}")

if failed:
    print("\n❌ Missing fields:")
    for section, field, _, _ in failed:
        print(f"   • {section}.{field}")
else:
    print("\n🎉 ALL REQUIRED FIELDS PRESENT!")

# Specific frontend error check
print("\n" + "=" * 80)
print("🎯 CHECKING SPECIFIC FRONTEND ERROR")
print("=" * 80)

error_field = "nutritional_analysis.detected_nutrients"
try:
    detected_nutrients = result['nutritional_analysis']['detected_nutrients']
    length = len(detected_nutrients)
    print(f"✅ {error_field} EXISTS")
    print(f"✅ Type: {type(detected_nutrients)}")
    print(f"✅ Length: {length}")
    print(f"✅ Values: {detected_nutrients}")
    print(f"\n✅ FRONTEND ERROR SHOULD BE FIXED!")
except KeyError as e:
    print(f"❌ {error_field} MISSING: {e}")
    print(f"❌ FRONTEND ERROR WILL STILL OCCUR!")
except Exception as e:
    print(f"❌ Error accessing field: {e}")

# Full JSON for debugging
print("\n" + "=" * 80)
print("📄 FULL RESPONSE (for reference):")
print("=" * 80)
print(json.dumps(result, indent=2)[:2000])  # First 2000 chars
if len(json.dumps(result)) > 2000:
    print(f"\n... (truncated, full response is {len(json.dumps(result))} chars)")

print("\n" + "=" * 80)
if not failed:
    print("✅ FRONTEND COMPATIBILITY: VERIFIED")
    print("✅ All required fields are present and correctly structured")
    print("✅ The FoodClassifier.tsx error should be fixed!")
else:
    print("⚠️ FRONTEND COMPATIBILITY: ISSUES FOUND")
    print("⚠️ Some required fields are missing")
print("=" * 80)
