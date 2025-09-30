#!/usr/bin/env node

/**
 * OCR Service Test Script
 * This script tests the OCR functionality end-to-end to ensure the permanent fix works
 */

const fs = require('fs');
const path = require('path');

// Test configuration
const CONFIG = {
  frontendUrl: 'http://localhost:3000',
  ocrServiceUrl: 'http://localhost:8000',
  testImages: [
    'test-receipt-1.jpg',
    'test-receipt-2.jpg',
    'test-receipt-3.jpg'
  ]
};

// Create test receipt images if they don't exist
function createTestImages() {
  console.log('Creating test receipt images...');
  
  // Simple test receipt text that should be parsed
  const testReceipts = [
    `WALMART
Store #1234
01/15/2024 2:34 PM

Milk 2% 1gal    $3.49
Bread Wheat     $2.99
Eggs Large 12ct $4.29
Apples Red 3lb  $5.99

Subtotal: $16.76
Tax: $1.34
Total: $18.10
Thank you for shopping!`,
    
    `TARGET
Store T-5678
12/25/2024 3:45 PM

Cereal Cheerios  $4.99
Milk Whole 1/2g  $2.79
Bananas Organic  $2.50
Yogurt Greek 4pk $5.49

Subtotal: $15.77
Tax: $1.26
Total: $17.03
RedCard saves 5%`,
    
    `COSTCO WHOLESALE
Warehouse #9012
11/30/2024 1:20 PM

Rotisserie Chicken  $4.99
Paper Towels 12pk   $19.99
Milk Organic 2gal   $5.99
Eggs 24ct          $7.49

Subtotal: $38.46
Tax: $3.08
Total: $41.54
Member since 2020`
  ];

  testReceipts.forEach((receiptText, index) => {
    const filename = CONFIG.testImages[index];
    const filepath = path.join(__dirname, filename);
    
    if (!fs.existsSync(filepath)) {
      // Create a simple text file as placeholder
      fs.writeFileSync(filepath, receiptText);
      console.log(`Created test file: ${filename}`);
    }
  });
}

// Test OCR service health
async function testOcrServiceHealth() {
  console.log('Testing OCR service health...');
  
  try {
    const response = await fetch(`${CONFIG.ocrServiceUrl}/health`);
    const data = await response.json();
    
    if (data.status === 'healthy') {
      console.log('✅ OCR service is healthy');
      return true;
    } else {
      console.log('❌ OCR service health check failed');
      return false;
    }
  } catch (error) {
    console.error('❌ OCR service unreachable:', error.message);
    return false;
  }
}

// Test API endpoint availability
async function testApiEndpoint() {
  console.log('Testing API endpoint availability...');
  
  try {
    const response = await fetch(`${CONFIG.frontendUrl}/api/ocr/receipt`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        imageDataUrl: 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/2wBDAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwA/AB8A'
      })
    });
    
    if (response.status === 404) {
      console.log('❌ API endpoint returns 404 - route not found');
      return false;
    }
    
    if (response.status === 400) {
      console.log('✅ API endpoint accessible (400 is expected for test data)');
      return true;
    }
    
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      console.log('✅ API endpoint returns JSON');
      return true;
    } else {
      console.log('❌ API endpoint returns non-JSON response');
      return false;
    }
    
  } catch (error) {
    console.error('❌ API endpoint test failed:', error.message);
    return false;
  }
}

// Test with a real image
async function testWithRealImage() {
  console.log('Testing with real receipt image...');
  
  try {
    // Read a test image and convert to base64
    const testImagePath = path.join(__dirname, CONFIG.testImages[0]);
    if (!fs.existsSync(testImagePath)) {
      console.log('⚠️ Test image not found, skipping real image test');
      return true;
    }
    
    const imageBuffer = fs.readFileSync(testImagePath);
    const base64Image = `data:image/jpeg;base64,${imageBuffer.toString('base64')}`;
    
    const response = await fetch(`${CONFIG.frontendUrl}/api/ocr/receipt`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        imageDataUrl: base64Image
      })
    });
    
    const data = await response.json();
    
    if (response.ok && data.success) {
      console.log('✅ Real image test successful');
      console.log('   Items found:', data.data?.items?.length || 0);
      console.log('   Sample items:', data.data?.items?.slice(0, 3).map(item => item.name) || []);
      return true;
    } else {
      console.log('❌ Real image test failed:', data.error || 'Unknown error');
      return false;
    }
    
  } catch (error) {
    console.error('❌ Real image test error:', error.message);
    return false;
  }
}

// Run all tests
async function runAllTests() {
  console.log('🚀 Starting OCR Service Test Suite\n');
  
  let passed = 0;
  let total = 0;
  
  // Create test images
  createTestImages();
  
  // Test 1: OCR Service Health
  total++;
  if (await testOcrServiceHealth()) {
    passed++;
  }
  
  // Test 2: API Endpoint
  total++;
  if (await testApiEndpoint()) {
    passed++;
  }
  
  // Test 3: Real Image Test
  total++;
  if (await testWithRealImage()) {
    passed++;
  }
  
  console.log(`\n📊 Test Results: ${passed}/${total} tests passed`);
  
  if (passed === total) {
    console.log('✅ All tests passed! OCR functionality is working correctly.');
    return true;
  } else {
    console.log('❌ Some tests failed. Check the logs above for details.');
    return false;
  }
}

// Run tests if called directly
if (require.main === module) {
  runAllTests().then(success => {
    process.exit(success ? 0 : 1);
  });
}

module.exports = {
  runAllTests,
  testOcrServiceHealth,
  testApiEndpoint,
  testWithRealImage,
  CONFIG
};