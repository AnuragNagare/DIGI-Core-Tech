"""
Quick test to see which classifier the API is using
"""

import requests
import json

print("🔍 Checking which classifier is loaded in the API...")

try:
    response = requests.get("http://127.0.0.1:8001/health", timeout=5)
    if response.status_code == 200:
        data = response.json()
        print("\n📊 Health Check Response:")
        print(json.dumps(data, indent=2))
    else:
        print(f"❌ Status: {response.status_code}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n🧪 Testing classification...")

# Use the pizza image
with open('test_pizza.jpg', 'rb') as f:
    img_bytes = f.read()

files = {'file': ('pizza.jpg', img_bytes, 'image/jpeg')}
response = requests.post("http://127.0.0.1:8001/classify-food", files=files, timeout=30)

if response.status_code == 200:
    result = response.json()
    print(f"\n✅ Classification result:")
    print(f"   Model type: {result.get('model_type', 'unknown')}")
    print(f"   Model name: {result.get('model_name', 'unknown')}")
    print(f"   Model classes: {result.get('model_classes', 'unknown')}")
    print(f"   Confidence: {result.get('confidence', 0) * 100:.1f}%")
    print(f"   Detected: {result['ingredients'][0]['name'] if result.get('ingredients') else 'None'}")
else:
    print(f"❌ Status: {response.status_code}")
