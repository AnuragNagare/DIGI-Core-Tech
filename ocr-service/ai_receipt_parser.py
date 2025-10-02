"""
AI-Powered Receipt Parser using OpenAI GPT-4 Vision
Works with ANY receipt format from anywhere in the world
Extracts ONLY actual food items, ignoring:
- Promotions (Buy One Get One, Special Offers)
- Modifiers (ADD Cream, NO Sugar, Extra Cheese)
- Totals, Subtotals, Tax
- Store info, dates, payment info
"""

import os
import logging
import base64
from typing import List, Dict, Any
import json
import openai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIReceiptParser:
    """
    Uses OpenAI GPT-4 Vision to intelligently parse receipts.
    Works with ANY receipt format worldwide.
    """
    
    def __init__(self):
        # Get API key from environment
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not set. AI parsing will be disabled.")
        
        openai.api_key = self.api_key
    
    def parse_receipt_with_ai(self, image_bytes: bytes, ocr_text: str = None) -> List[Dict[str, Any]]:
        """
        Parse receipt using GPT-4 Vision.
        
        Args:
            image_bytes: Receipt image as bytes
            ocr_text: Optional OCR text (can help but not required)
            
        Returns:
            List of food items with name, quantity, and price
        """
        if not self.api_key:
            logger.error("OpenAI API key not configured")
            return []
        
        try:
            # Convert image to base64
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            
            # Prepare messages for GPT-4 Vision
            messages = [
                {
                    "role": "system",
                    "content": """You are an expert receipt analyzer. Your task is to extract ONLY the actual food/beverage items that were purchased.

IMPORTANT RULES:
1. Extract ONLY main food/beverage items (things people eat or drink)
2. IGNORE promotions like "Buy One Get One", "Special Offer", "Deal"
3. IGNORE modifiers like "ADD Cream", "NO Sugar", "Extra Cheese", "Hold Onions"
4. IGNORE totals, subtotals, tax, GST, tips
5. IGNORE store info, dates, times, payment methods
6. IGNORE quantity descriptors alone like "2x", "3 items"

For each ACTUAL FOOD ITEM, extract:
- name: The food/beverage name (clean, without modifiers)
- quantity: How many were ordered (default 1)
- price: The price for this item

Return ONLY valid JSON array: [{"name": "...", "quantity": 1, "price": 3.99}, ...]"""
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Extract ONLY the actual food/beverage items from this receipt. Return as JSON array."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ]
            
            # Add OCR text if available (helps with accuracy)
            if ocr_text:
                messages.append({
                    "role": "user",
                    "content": f"Here's also the OCR text from the receipt:\n{ocr_text}\n\nPlease extract only actual food items."
                })
            
            logger.info("🤖 Sending receipt to GPT-4 Vision for analysis...")
            
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-4-vision-preview",
                messages=messages,
                max_tokens=1000,
                temperature=0.1  # Low temperature for consistent results
            )
            
            # Parse response
            content = response.choices[0].message.content
            logger.info(f"📝 GPT-4 Vision response: {content}")
            
            # Extract JSON from response
            # Handle markdown code blocks
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0].strip()
            else:
                json_str = content.strip()
            
            # Parse JSON
            items = json.loads(json_str)
            
            logger.info(f"✅ Extracted {len(items)} items using AI")
            for item in items:
                logger.info(f"  - {item['name']}: ${item.get('price', 0):.2f} (qty: {item.get('quantity', 1)})")
            
            return items
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            logger.error(f"Response content: {content}")
            return []
        except Exception as e:
            logger.error(f"AI parsing failed: {e}")
            return []
    
    def fallback_to_intelligent_parser(self, ocr_text: str) -> List[Dict[str, Any]]:
        """
        Fallback to intelligent rule-based parser if AI is not available.
        """
        from intelligent_receipt_parser import receipt_parser
        return receipt_parser.parse_receipt_items(ocr_text)


# Global instance
ai_parser = AIReceiptParser()
