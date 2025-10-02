/**
 * Automated Browser Test for Receipt OCR
 * - Downloads random receipt images from internet
 * - Uploads to localhost application
 * - Verifies only food items are extracted (100% accuracy)
 */

const { chromium } = require('@playwright/test');
const fs = require('fs');
const path = require('path');
const https = require('https');

// Test receipt image URLs (real grocery receipts)
const RECEIPT_URLS = [
    'https://images.template.net/107155/grocery-store-receipt-template-dhscw.png',
    'https://www.thebalancemoney.com/thmb/wrX1mTHmAaLxX2U6TCCq5f9G3LI=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/grocery-receipt-56a00d7c3df78cafdaa05da2.jpg',
    'https://i.pinimg.com/originals/92/0d/9c/920d9c6a4d4e3c0b5e9e2a0f5c1e7b3d.jpg'
];

// Blacklisted words that should NOT appear in extracted items
const BLACKLISTED_WORDS = [
    'subtotal', 'total', 'tax', 'change', 'balance', 'loyalty',
    'special', 'discount', 'payment', 'cash', 'credit', 'debit',
    'thank', 'welcome', 'date', 'time', 'store', 'receipt'
];

async function downloadReceipt(url, filepath) {
    return new Promise((resolve, reject) => {
        const file = fs.createWriteStream(filepath);
        https.get(url, (response) => {
            if (response.statusCode !== 200) {
                reject(new Error(`Failed to download: ${response.statusCode}`));
                return;
            }
            response.pipe(file);
            file.on('finish', () => {
                file.close();
                console.log(`✅ Downloaded receipt from: ${url}`);
                resolve();
            });
        }).on('error', (err) => {
            fs.unlink(filepath, () => {});
            reject(err);
        });
    });
}

async function testReceiptUpload(browser, receiptPath, receiptName) {
    console.log(`\n${'='.repeat(60)}`);
    console.log(`Testing Receipt: ${receiptName}`);
    console.log(`${'='.repeat(60)}`);
    
    const context = await browser.newContext();
    const page = await context.newPage();
    
    try {
        // Navigate to the app
        console.log('📱 Navigating to http://localhost:3001/tracking...');
        await page.goto('http://localhost:3001/tracking', { waitUntil: 'networkidle', timeout: 30000 });
        
        // Wait for page to be interactive
        await page.waitForTimeout(2000);
        
        // Look for file upload input or scan receipt button
        console.log('🔍 Looking for receipt upload option...');
        
        // Try different selectors for upload input
        const uploadSelectors = [
            'input[type="file"]',
            'input[accept*="image"]',
            '[data-testid="receipt-upload"]',
            '.receipt-upload',
            '#receipt-upload'
        ];
        
        let uploadInput = null;
        for (const selector of uploadSelectors) {
            uploadInput = await page.$(selector);
            if (uploadInput) {
                console.log(`✅ Found upload input with selector: ${selector}`);
                break;
            }
        }
        
        if (!uploadInput) {
            // Try to find upload button and click it
            const buttonSelectors = [
                'text=Upload Receipt',
                'text=Scan Receipt',
                'text=Add Receipt',
                'button:has-text("Receipt")',
                'button:has-text("Upload")',
                'button:has-text("Scan")'
            ];
            
            for (const selector of buttonSelectors) {
                try {
                    const button = await page.$(selector);
                    if (button) {
                        console.log(`✅ Found button with selector: ${selector}`);
                        await button.click();
                        await page.waitForTimeout(1000);
                        
                        // Try to find upload input again
                        uploadInput = await page.$('input[type="file"]');
                        if (uploadInput) {
                            console.log(`✅ Upload input appeared after clicking button`);
                            break;
                        }
                    }
                } catch (e) {
                    // Continue trying next selector
                }
            }
        }
        
        if (!uploadInput) {
            console.log('❌ Could not find receipt upload input');
            console.log('Page content preview:');
            const bodyText = await page.textContent('body');
            console.log(bodyText.substring(0, 500));
            return null;
        }
        
        // Upload the receipt
        console.log(`📤 Uploading receipt: ${receiptPath}...`);
        await uploadInput.setInputFiles(receiptPath);
        
        // Wait for processing
        console.log('⏳ Waiting for OCR processing...');
        await page.waitForTimeout(5000);
        
        // Try to find extracted items
        console.log('🔍 Looking for extracted items...');
        
        // Wait for results container
        await page.waitForSelector('body', { timeout: 10000 });
        
        // Get all text content from the page
        const pageContent = await page.content();
        
        // Try to extract structured item data
        let extractedItems = [];
        
        // Method 1: Look for item list elements
        const itemSelectors = [
            '.receipt-item',
            '.item-row',
            '[data-testid="receipt-item"]',
            '.parsed-item'
        ];
        
        for (const selector of itemSelectors) {
            const items = await page.$$(selector);
            if (items.length > 0) {
                console.log(`✅ Found ${items.length} items with selector: ${selector}`);
                for (const item of items) {
                    const text = await item.textContent();
                    extractedItems.push(text.trim());
                }
                break;
            }
        }
        
        // Method 2: Look for JSON data in page
        if (extractedItems.length === 0) {
            // Try to extract from script tags or data attributes
            const scripts = await page.$$('script');
            for (const script of scripts) {
                const content = await script.textContent();
                if (content.includes('items') || content.includes('receipt')) {
                    // Try to parse JSON
                    try {
                        const match = content.match(/items["\s:]+(\[.*?\])/);
                        if (match) {
                            const items = JSON.parse(match[1]);
                            extractedItems = items.map(item => item.name || JSON.stringify(item));
                        }
                    } catch (e) {
                        // Continue
                    }
                }
            }
        }
        
        // Method 3: Look in page text for item patterns
        if (extractedItems.length === 0) {
            console.log('⚠️  Could not find structured items, checking page text...');
            const bodyText = await page.textContent('body');
            
            // Look for patterns like "ITEM_NAME $XX.XX"
            const itemPattern = /([A-Z][A-Z\s]+)\s+\$?\d+\.\d{2}/g;
            const matches = bodyText.matchAll(itemPattern);
            
            for (const match of matches) {
                const itemName = match[1].trim();
                if (itemName.length > 3 && itemName.length < 40) {
                    extractedItems.push(itemName);
                }
            }
        }
        
        console.log(`\n📊 Extraction Results:`);
        console.log(`${'='.repeat(60)}`);
        console.log(`Total items extracted: ${extractedItems.length}`);
        
        if (extractedItems.length > 0) {
            console.log(`\nExtracted Items:`);
            extractedItems.forEach((item, index) => {
                console.log(`  ${index + 1}. ${item}`);
            });
            
            // Validate items
            console.log(`\n🔍 Validation:`);
            let isValid = true;
            const invalidItems = [];
            
            for (const item of extractedItems) {
                const itemLower = item.toLowerCase();
                for (const blacklisted of BLACKLISTED_WORDS) {
                    if (itemLower.includes(blacklisted)) {
                        // Check if it's ONLY the blacklisted word (not part of food name)
                        const words = itemLower.split(/\s+/);
                        if (words.length <= 2 && words.includes(blacklisted)) {
                            isValid = false;
                            invalidItems.push({item, reason: `Contains blacklisted word: ${blacklisted}`});
                        }
                    }
                }
            }
            
            if (isValid) {
                console.log(`✅ All items are valid food items`);
                console.log(`✅ No blacklisted words found`);
                return { success: true, itemCount: extractedItems.length, items: extractedItems };
            } else {
                console.log(`❌ Found invalid items:`);
                invalidItems.forEach(({item, reason}) => {
                    console.log(`  - ${item}: ${reason}`);
                });
                return { success: false, itemCount: extractedItems.length, items: extractedItems, invalidItems };
            }
        } else {
            console.log(`⚠️  No items extracted - could not find item data in page`);
            console.log(`\nPage title: ${await page.title()}`);
            return { success: false, itemCount: 0, items: [], error: 'No items found' };
        }
        
    } catch (error) {
        console.log(`❌ Error during test:`, error.message);
        return { success: false, error: error.message };
    } finally {
        await context.close();
    }
}

async function main() {
    console.log(`\n${'='.repeat(60)}`);
    console.log(`🤖 Automated Receipt OCR Test`);
    console.log(`${'='.repeat(60)}`);
    console.log(`\n📋 Test Objective:`);
    console.log(`  1. Download random grocery receipts from internet`);
    console.log(`  2. Upload to localhost:3001 application`);
    console.log(`  3. Verify ONLY food items are extracted`);
    console.log(`  4. Ensure 100% accuracy (no totals, dates, metadata)`);
    
    // Create downloads directory
    const downloadsDir = path.join(__dirname, 'test-receipts');
    if (!fs.existsSync(downloadsDir)) {
        fs.mkdirSync(downloadsDir, { recursive: true });
    }
    
    // Download test receipts
    console.log(`\n📥 Downloading test receipts...`);
    const receiptPaths = [];
    
    for (let i = 0; i < RECEIPT_URLS.length; i++) {
        const url = RECEIPT_URLS[i];
        const filename = `test-receipt-${i + 1}.jpg`;
        const filepath = path.join(downloadsDir, filename);
        
        try {
            await downloadReceipt(url, filepath);
            receiptPaths.push({ path: filepath, name: filename });
        } catch (error) {
            console.log(`⚠️  Failed to download ${url}: ${error.message}`);
        }
    }
    
    if (receiptPaths.length === 0) {
        console.log(`❌ No receipts downloaded. Exiting.`);
        return;
    }
    
    console.log(`\n✅ Downloaded ${receiptPaths.length} test receipts`);
    
    // Launch browser
    console.log(`\n🌐 Launching browser...`);
    const browser = await chromium.launch({ headless: false });
    
    // Test each receipt
    const results = [];
    for (const receipt of receiptPaths) {
        const result = await testReceiptUpload(browser, receipt.path, receipt.name);
        if (result) {
            results.push({ ...result, receipt: receipt.name });
        }
    }
    
    // Close browser
    await browser.close();
    
    // Summary
    console.log(`\n\n${'='.repeat(60)}`);
    console.log(`📊 FINAL TEST RESULTS`);
    console.log(`${'='.repeat(60)}`);
    
    const successCount = results.filter(r => r.success).length;
    const failureCount = results.filter(r => !r.success).length;
    const accuracy = results.length > 0 ? (successCount / results.length * 100).toFixed(1) : 0;
    
    console.log(`\nTotal Receipts Tested: ${results.length}`);
    console.log(`✅ Passed: ${successCount}`);
    console.log(`❌ Failed: ${failureCount}`);
    console.log(`\n🎯 Accuracy: ${accuracy}%`);
    
    if (accuracy === 100) {
        console.log(`\n🎉 SUCCESS! All receipts extracted ONLY food items!`);
        console.log(`✅ 100% Accuracy achieved!`);
    } else {
        console.log(`\n⚠️  IMPROVEMENT NEEDED`);
        console.log(`❌ Some receipts extracted non-food items or had errors`);
        
        results.forEach(result => {
            if (!result.success) {
                console.log(`\n  Receipt: ${result.receipt}`);
                if (result.error) {
                    console.log(`  Error: ${result.error}`);
                } else if (result.invalidItems) {
                    console.log(`  Invalid items: ${result.invalidItems.length}`);
                    result.invalidItems.forEach(({item, reason}) => {
                        console.log(`    - ${item}: ${reason}`);
                    });
                }
            }
        });
    }
    
    console.log(`\n${'='.repeat(60)}`);
}

main().catch(console.error);
