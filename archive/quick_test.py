#!/usr/bin/env python3
"""
Quick OCR Test Script
"""

import requests
import json

def quick_test():
    """Quick test of the enhanced OCR service."""
    
    base_url = "http://localhost:8000"
    
    print("🔍 Quick OCR Service Test")
    print("=" * 30)
    
    # Test health
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health: OK")
        else:
            print(f"❌ Health: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return
    
    # Test sample receipt
    try:
        response = requests.get(f"{base_url}/test", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Sample Test: OK")
                print("\n📋 Sample Receipt:")
                print(data.get('formattedDisplay', ''))
            else:
                print(f"❌ Sample test failed: {data.get('error')}")
        else:
            print(f"❌ Sample test: {response.status_code}")
    except Exception as e:
        print(f"❌ Sample test failed: {e}")

if __name__ == "__main__":
    quick_test()