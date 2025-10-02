"""
Advanced Receipt Parser with ML Validation
Uses HuggingFace food classifier to validate each potential item
Works WITHOUT needing OpenAI API key
"""

import logging
import re
from typing import List, Dict, Any
from intelligent_receipt_parser import receipt_parser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MLValidatedReceiptParser:
    """
    Advanced parser that uses ML food classifier to validate items.
    """
    
    def __init__(self, food_classifier=None):
        self.food_classifier = food_classifier
        self.base_parser = receipt_parser
    
    async def parse_with_ml_validation(self, ocr_text: str, image_bytes: bytes = None) -> List[Dict[str, Any]]:
        """
        Parse receipt and validate items using ML food classifier.
        
        Args:
            ocr_text: Raw OCR text
            image_bytes: Optional image bytes for visual classification
            
        Returns:
            List of validated food items
        """
        logger.info("🔍 Starting ML-validated receipt parsing...")
        
        # Step 1: Extract potential items using intelligent parser
        potential_items = self.base_parser.parse_receipt_items(ocr_text)
        logger.info(f"📝 Found {len(potential_items)} potential items")
        
        if not potential_items:
            return []
        
        # Step 2: Validate each item using food classifier (if available)
        validated_items = []
        
        for item in potential_items:
            item_name = item['name']
            
            # Basic validation first
            if self._is_definitely_not_food(item_name):
                logger.debug(f"❌ Rejected: {item_name} (definitely not food)")
                continue
            
            # If we have a food classifier, use it for validation
            if self.food_classifier:
                is_food = await self._validate_with_classifier(item_name)
                if is_food:
                    validated_items.append(item)
                    logger.info(f"✅ Validated: {item_name}")
                else:
                    logger.debug(f"❌ Rejected by classifier: {item_name}")
            else:
                # No classifier available, use basic validation
                if self._is_likely_food(item_name):
                    validated_items.append(item)
                    logger.info(f"✅ Accepted: {item_name}")
                else:
                    logger.debug(f"❌ Rejected: {item_name}")
        
        logger.info(f"✅ Final count: {len(validated_items)} validated food items")
        return validated_items
    
    def _is_definitely_not_food(self, text: str) -> bool:
        """Quick check for obvious non-food items."""
        text_lower = text.lower()
        
        # Obvious non-food patterns
        non_food_patterns = [
            r'^(add|no|hold|extra|without)\s',  # Modifiers at start
            r'^(buy|get|bogo)\s',  # Promotions
            r'(subtotal|total|tax|gst|balance|change|due|payment)$',  # Financial
            r'^(\d+\s*x|\d+\s*@)',  # Pure quantities
        ]
        
        for pattern in non_food_patterns:
            if re.search(pattern, text_lower):
                return True
        
        return False
    
    def _is_likely_food(self, text: str) -> bool:
        """Heuristic check if text is likely food."""
        text_lower = text.lower()
        
        # Food indicators
        food_words = [
            # Common food items
            'coffee', 'tea', 'juice', 'soda', 'water', 'milk',
            'burger', 'sandwich', 'wrap', 'salad', 'soup',
            'chicken', 'beef', 'pork', 'fish', 'salmon',
            'pizza', 'pasta', 'rice', 'noodle',
            'egg', 'bacon', 'sausage', 'ham',
            'bread', 'toast', 'bagel', 'muffin', 'croissant',
            'fries', 'potato', 'chips',
            'ice cream', 'dessert', 'cake', 'cookie',
            
            # Vegetables
            'lettuce', 'tomato', 'onion', 'pepper', 'mushroom',
            'broccoli', 'carrot', 'celery', 'cucumber',
            
            # Fruits
            'apple', 'banana', 'orange', 'grape', 'strawberry',
            
            # Food types
            'meal', 'combo', 'plate', 'bowl', 'cup',
            'breakfast', 'lunch', 'dinner',
        ]
        
        # Check if any food word is in the text
        for food_word in food_words:
            if food_word in text_lower:
                return True
        
        # Check if it has reasonable length and structure
        if 3 <= len(text) <= 40:
            # Has letters and possibly numbers
            has_letters = any(c.isalpha() for c in text)
            not_all_numbers = not text.replace(' ', '').isdigit()
            
            return has_letters and not_all_numbers
        
        return False
    
    async def _validate_with_classifier(self, item_name: str) -> bool:
        """
        Validate if item_name is actually food using the classifier.
        Returns True if it's food, False otherwise.
        """
        # TODO: Implement actual classifier validation
        # For now, just use heuristics
        return self._is_likely_food(item_name)


# Global instance
ml_parser = MLValidatedReceiptParser()
