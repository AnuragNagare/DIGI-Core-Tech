"""
Detailed test with error checking
"""

import requests
import json

print("🧪 Detailed API Test\n")

# Load pizza image
with open('test_pizza.jpg', 'rb') as f:
    img_data = f.read()

print(f"📁 Image size: {len(img_data)} bytes")

# Send request
url = "http://127.0.0.1:8001/classify-food"
files = {'file': ('pizza.jpg', img_data, 'image/jpeg')}

print(f"📤 Sending POST to {url}")

try:
    response = requests.post(url, files=files, timeout=30)
    
    print(f"📥 Response status: {response.status_code}")
    print(f"📄 Response headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ JSON Response:")
        print(json.dumps(data, indent=2))
    else:
        print(f"\n❌ Error response:")
        print(response.text)
        
except Exception as e:
    print(f"\n❌ Exception: {e}")
    import traceback
    traceback.print_exc()
