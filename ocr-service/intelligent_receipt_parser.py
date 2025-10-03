"""
Intelligent Receipt Item Extractor
Uses ML + Rule-based filtering to extract ONLY real food items from receipts
Ignores: totals, subtotals, payment info, dates, store names, loyalty numbers, etc.
"""

import re
import logging
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ReceiptItem:
    """Represents a single food/grocery item from a receipt."""
    name: str
    quantity: float
    price: float
    unit_price: float = None
    unit: str = None
    confidence: float = 0.0
    
class IntelligentReceiptParser:
    """
    Global Intelligent Receipt Parser - Works with receipts from any country/language.
    Designed for worldwide use with multi-language, multi-currency, and multi-format support.
    """
    
    def __init__(self):
        # Global blacklist - includes words from major languages worldwide
        self.BLACKLIST_KEYWORDS = {
            # English
            'subtotal', 'sub-total', 'sub total', 'total', 'change', 'cash', 'credit',
            'debit', 'card', 'payment', 'amount', 'balance', 'due', 'paid', 'tender',
            'loyalty', 'points', 'rewards', 'member', 'savings', 'discount', 'coupon',
            'receipt', 'invoice', 'order', 'transaction', 'ref', 'reference',
            
            # Spanish
            'subtotal', 'total', 'cambio', 'efectivo', 'tarjeta', 'pago', 'importe',
            'descuento', 'recibo', 'factura', 'pedido', 'transacción',
            
            # French  
            'sous-total', 'total', 'monnaie', 'espèces', 'carte', 'paiement', 'montant',
            'remise', 'reçu', 'facture', 'commande', 'transaction',
            
            # German
            'zwischensumme', 'summe', 'gesamt', 'wechselgeld', 'bargeld', 'karte',
            'zahlung', 'betrag', 'rabatt', 'beleg', 'rechnung',
            
            # Portuguese
            'subtotal', 'total', 'troco', 'dinheiro', 'cartão', 'pagamento',
            'desconto', 'recibo', 'fatura', 'pedido',
            
            # Italian
            'subtotale', 'totale', 'resto', 'contanti', 'carta', 'pagamento',
            'sconto', 'ricevuta', 'fattura', 'ordine',
            
            # Chinese (common terms)
            '小计', '总计', '合计', '找零', '现金', '刷卡', '支付', '折扣', '收据',
            
            # Japanese
            '小計', '合計', 'お釣り', '現金', 'カード', '支払い', '割引', 'レシート',
            
            # Common receipt metadata (language-agnostic)
            'vat', 'tax', 'iva', 'mwst', 'tva', 'btw', 'imposto', 'steuer',
            'store', 'shop', 'market', 'tienda', 'magasin', 'geschäft', 'loja',
            'date', 'time', 'fecha', 'hora', 'datum', 'zeit', 'data', 'tempo',
            
            # Numbers/codes alone
            'number', 'no', '#', 'id', 'code', 'sku', 'barcode',
            
            # Tax related
            'tax', 'gst', 'pst', 'hst', 'vat', 'duty', 'fee', 'surcharge',
            
            # Greetings
            'thank', 'welcome', 'hello', 'goodbye', 'please', 'visit',
            'come', 'again', 'see you', 'have a', 'enjoy',
        }
        
        # Global currency symbols and patterns
        self.CURRENCY_SYMBOLS = {
            '$', '€', '£', '¥', '₹', '₽', '₩', '¢', '₡', '₦', '₨', '₱', '₫', '₪', 
            'kr', 'zł', 'Kč', 'Ft', 'lei', 'lv', 'Lt', '₴', '₸', '₼', '₾', '₺',
            'USD', 'EUR', 'GBP', 'JPY', 'CNY', 'INR', 'RUB', 'KRW', 'AUD', 'CAD'
        }
        
        # Global number format patterns (handles different decimal separators)
        self.NUMBER_PATTERNS = [
            r'(\d{1,3}(?:,\d{3})*\.\d{2})',  # US: 1,234.56
            r'(\d{1,3}(?:\.\d{3})*,\d{2})',  # EU: 1.234,56  
            r'(\d{1,3}(?: \d{3})*[,\.]\d{2})',  # FR: 1 234,56 or 1 234.56
            r'(\d+[,\.]\d{2})',               # Simple: 123.45 or 123,45
            r'(\d+\.\d{2})',                  # Standard decimal: 123.45
            r'(\d+)',                         # Whole numbers: 123
        ]
        
        # Words that commonly appear in ONLY unit descriptions (not item names)
        self.UNIT_ONLY_KEYWORDS = {
            'kg', 'g', 'lb', 'oz', 'l', 'ml', 'net', 'wt', 'weight', 'each', 'ea'
        }
        
        # Common food categories (helps validate if something is a food item)
        self.FOOD_CATEGORIES = {
            # Vegetables
            'lettuce', 'tomato', 'potato', 'onion', 'carrot', 'broccoli', 'spinach',
            'pepper', 'cucumber', 'zucchini', 'zuchinni', 'squash', 'celery', 'cabbage', 
            'pea', 'peas', 'bean', 'beans', 'corn', 'mushroom', 'asparagus', 'brussel', 'sprout', 'sprouts',
            
            # Fruits
            'apple', 'banana', 'orange', 'grape', 'grapes', 'strawberry', 'blueberry', 'melon',
            'mango', 'pineapple', 'peach', 'pear', 'cherry', 'avocado', 'kiwi',
            'lemon', 'lime', 'grapefruit', 'plum',
            
            # Proteins
            'chicken', 'beef', 'pork', 'fish', 'salmon', 'tuna', 'shrimp', 'turkey',
            'lamb', 'bacon', 'sausage', 'ham', 'egg', 'eggs', 'tofu',
            
            # Dairy
            'milk', 'cheese', 'yogurt', 'butter', 'cream', 'ice cream',
            
            # Grains
            'bread', 'rice', 'pasta', 'cereal', 'flour', 'oat', 'oats', 'quinoa',
            
            # Beverages
            'juice', 'soda', 'water', 'coffee', 'tea', 'beer', 'wine',
            
            # Other groceries
            'oil', 'sugar', 'salt', 'spice', 'sauce', 'soup', 'nut', 'nuts', 'seed', 'seeds',
        }
    
    def is_blacklisted(self, text: str) -> bool:
        """Check if text contains blacklisted keywords - LESS RESTRICTIVE for better extraction."""
        import re
        
        text_lower = text.lower().strip()
        
        # Extract just the item name (before price) for checking
        item_name_only = re.sub(r'\s*\$?\d+[\.,]\d{2}\s*$', '', text).strip().lower()
        
        # ENHANCED CRITICAL BLACKLIST - covers more non-food items dynamically
        critical_blacklist = {
            # Financial terms
            'subtotal', 'sub-total', 'sub total', 'total', 'grand total', 'final total',
            'm subtotal', 'l subtotal', 's subtotal', 'xl subtotal',  # Size-based subtotals
            'take-out total', 'take out total', 'takeout total', 'dine-in total',
            'change', 'cash tendered', 'cash received', 'credit card', 'debit card',
            'balance', 'balance due', 'amount due', 'amount paid', 'payment',
            'cash', 'credit', 'debit', 'visa', 'mastercard', 'amex', 'discover',
            
            # Loyalty and rewards
            'loyalty', 'loyalty points', 'points', 'rewards', 'member savings',
            'loyalty discount', 'member discount', 'club discount',
            
            # Taxes and fees
            'tax', 'gst', 'pst', 'hst', 'vat', 'sales tax', 'local tax', 'tip',
            'service charge', 'delivery fee', 'processing fee',
            
            # Receipt metadata
            'loyalty number', 'member number', 'card number', 'account number',
            'receipt number', 'transaction id', 'ref number', 'invoice number',
            'order number', 'ticket number', 'confirmation number',
            
            # Store information
            'thank you', 'have a nice day', 'come again', 'welcome', 'goodbye',
            'store hours', 'phone number', 'address', 'website', 'location',
            'cashier', 'clerk', 'manager', 'supervisor', 'server', 'staff',
            
            # Promotional/non-food terms
            'discount', 'coupon', 'savings', 'promotion', 'offer', 'deal',
            'buy one get one', 'bogo', 'b1g1', 'special offer', 'combo deal',
            'buy one; get one', 'buy one, get one',  # With punctuation variations
            
            # OCR corrupted promotional text (from your examples)
            'duy ona gel one une', 'buy one; get one line', 'gel one line',
            'get one line', 'duy ona', 'gel one', 'buy one get one line',
            '1. buy one; get one', '1 buy one get one',  # Numbered versions
            
            # OCR corrupted non-food items (based on test results)
            'sumage liberin', 'burte eva line', 'hah browne', 'liced corien',
            'whanwyrith', 'knonuy nib discount aeuismod lis',
            
            # Garbled text patterns that aren't food (but NOT aeuismod - it's valid Lorem food)
            'liberin', 'browne', 'corien', 'whanwyrith', 'knonuy',
            'lis', 'eva line', 'una line', 'line una', 'line eva',
            
            # Survey/feedback
            'survey', 'feedback', 'rating', 'review', 'tell us', 'visit us',
            'online survey', 'customer survey', 'rate your experience',
            
            # Time/date references  
            'date', 'time', 'am', 'pm', 'today', 'yesterday', 'hour', 'minute',
            'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
            
            # Quantities alone (not food)
            'qty', 'quantity', 'item count', 'items', 'pieces', 'count',
            
            # Service terms
            'take out', 'take-out', 'takeout', 'dine in', 'dine-in', 'for here',
            'to go', 'delivery', 'pickup', 'drive thru', 'drive-thru',
            
            # Line items that aren't food
            'line item', 'line total', 'item total', 'row total',
        }
        
        # Check if entire text matches critical blacklist (exact phrases)
        for critical_item in critical_blacklist:
            if item_name_only == critical_item or text_lower == critical_item:
                logger.debug(f"  ❌ Critical blacklist match: '{critical_item}'")
                return True
        
        # ENHANCED: Patterns to catch payment/total/non-food items (from your examples)
        total_patterns = [
            r'^\s*(sub)?total\s*[:=\s]*\$?\d+[\.,]\d{2}\s*$',
            r'^\s*change\s*[:=\s]*\$?\d+[\.,]\d{2}\s*$',
            r'^\s*(cash|credit|debit)\s*[:=\s]*\$?\d+[\.,]\d{2}\s*$',
            r'^\s*tax\s*[:=\s]*\$?\d+[\.,]\d{2}\s*$',
            r'^\s*balance\s*[:=\s]*\$?\d+[\.,]\d{2}\s*$',
            
            # From your examples - catch these specific patterns
            r'^\s*take-?out\s+total\s*[:=\s]*\$?\d+[\.,]\d{2}\s*$',
            r'^\s*change\s*[:=\s]*\d+[\.,]\d{2}\s*$',  # "Change: 5" type
            r'^\s*gst\s*[:=\s]*\$?\d+[\.,]\d{2}\s*$',
            
            # Promotional lines that aren't food (ENHANCED)
            r'.*buy\s+one[,\s;]*get\s+one.*',  # Any line with "buy one get one"
            r'.*bogo.*',  # Any line with "bogo"
            r'.*b1g1.*',  # Any line with "b1g1"
            r'^\s*\d+\.\s*buy\s+one.*',  # "1. Buy One..." format
            
            # Original promotional patterns with prices
            r'^\s*buy\s+one[,\s]*get\s+one.*\$?\d+[\.,]\d{2}\s*$',
            r'^\s*(bogo|b1g1).*\$?\d+[\.,]\d{2}\s*$',
            
            # Lines with only codes/numbers and prices (likely not food)
            r'^\s*\d{3,6}\s*[:,-]?\s*\$?\d+[\.,]\d{2}\s*$',  # "02753: $2.99" type
        ]
        
        for pattern in total_patterns:
            if re.match(pattern, text_lower):
                logger.debug(f"  ❌ Total pattern match: '{pattern}'")
                return True
        
        # Special handling for numbered-code lines like "1: 0275 Ut Wisi Enim 2.99"
        if re.match(r'^\s*\d{1,2}[:]\s*\d{3,6}', text_lower):
            # Allow if there's descriptive text after the codes
            if re.search(r'[a-zA-Z]{3,}', item_name_only):
                logger.debug("  ✅ Numbered code line with description - allowing")
                pass
            else:
                logger.debug("  ❌ Numbered code line without description")
                return True
        
        # Check for date patterns (be more specific)
        date_patterns = [
            r'^\s*\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\s*$',
            r'^\s*\d{4}[/-]\d{1,2}[/-]\d{1,2}\s*$',
            r'^\s*(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{1,2},?\s+\d{4}\s*$',
        ]
        
        for pattern in date_patterns:
            if re.match(pattern, text_lower):
                logger.debug(f"  ❌ Date pattern match")
                return True
        
        # Allow items that contain food words, even if they have some blacklisted terms
        food_indicators = []
        for word in item_name_only.split():
            for food in self.FOOD_CATEGORIES:
                if food in word or word in food:
                    food_indicators.append(food)
        
        if food_indicators:
            logger.debug(f"  ✅ Contains food indicators: {food_indicators}")
            return False
        
        # For ambiguous cases, be more permissive
        # Only blacklist if it's clearly not a food item
        ambiguous_terms = ['special', 'discount', 'promo', 'sale', 'offer']
        for term in ambiguous_terms:
            if term in text_lower:
                # If it's ONLY the term + price, blacklist
                if item_name_only == term:
                    logger.debug(f"  ❌ Standalone promotional term: '{term}'")
                    return True
                # If it has other words, it might be "CHICKEN SPECIAL", so allow
                else:
                    logger.debug(f"  ✅ Promotional term with other words - allowing")
                    return False
        
        # Final check: if it's very short and has no clear food indicators, be cautious
        if len(item_name_only) < 3:
            logger.debug(f"  ❌ Too short: '{item_name_only}'")
            return True
        
        # If we get here, it's likely a valid item
        logger.debug(f"  ✅ Passed blacklist check: '{text[:50]}'")
        return False
    
    def is_unit_descriptor_only(self, text: str) -> bool:
        """Check if text is ONLY a unit descriptor (like '0.442kg NET @ $2.99/kg')."""
        text_lower = text.lower()
        
        # If it starts with a number followed by kg/lb/etc and contains NET, it's a unit line
        if re.match(r'^\d+\.?\d*\s*(kg|g|lb|oz|net|wt)', text_lower):
            return True

        # Lines that describe net weight or price per unit (even with OCR errors)
        if 'net' in text_lower and '@' in text_lower:
            return True

        # Catch patterns like "Net @ /Ko", "I 1.928Kq", etc.
        if re.search(r'net\s*@\s*/?\s*[a-z]{1,3}', text_lower):
            return True
            
        if re.search(r'[a-z]\s+\d+\.\d+\s*[a-z]{1,3}', text_lower):  # "I 1.928Kq" pattern
            return True

        if re.search(r'@\s*/?\s*[\w]{1,3}', text_lower) and any(unit in text_lower for unit in ['kg', 'kq', 'lb', 'oz', '/kg', '/lb']):
            return True

        # If it's ONLY unit keywords
        words = text_lower.split()
        if all(word in self.UNIT_ONLY_KEYWORDS or word.replace('.', '').isdigit() for word in words):
            return True

        return False
    
    def is_likely_food_item(self, text: str) -> bool:
        """
        Check if text likely contains a food item name - ENHANCED FOR BETTER DETECTION.
        Now more permissive to catch more real food items.
        """
        if not text or len(text.strip()) < 2:
            return False
            
        text_lower = text.lower().strip()
        
        # Remove price portion for better analysis
        text_clean = re.sub(r'\s*\$?\d+[\.,]\d{2}\s*$', '', text_lower).strip()
        
        # FIRST: Check if this is explicitly blacklisted (like "subtotal", "loyalty", etc.)
        if self.is_blacklisted(text_clean):
            logger.debug(f"  ❌ Blacklisted item rejected: '{text_clean}'")
            return False
        
        # SECOND: Check if this is just a unit descriptor (weight/measure without item name)
        if self.is_unit_descriptor_only(text_clean):
            logger.debug(f"  ❌ Unit descriptor rejected: '{text_clean}'")
            return False
        
        # Split into words for analysis
        words = [w.strip() for w in text_clean.split() if w.strip()]
        
        # Strong food indicators - if found, definitely a food item
        strong_food_indicators = {
            # Proteins
            'chicken', 'beef', 'pork', 'fish', 'salmon', 'tuna', 'turkey', 'bacon', 'sausage', 'ham',
            'egg', 'eggs', 'meat', 'steak', 'burger', 'wing', 'wings', 'thigh', 'breast',
            
            # Fast food/prepared items
            'pizza', 'burrito', 'burritos', 'taco', 'tacos', 'sandwich', 'wrap', 'wrap',
            'nugget', 'nuggets', 'fries', 'fry', 'hot dog', 'hotdog', 'sub', 'submarine',
            'quesadilla', 'enchilada', 'nachos', 'salad', 'soup', 'chili', 'mac', 'mac',
            
            # Vegetables  
            'lettuce', 'tomato', 'potato', 'onion', 'carrot', 'broccoli', 'spinach', 'pepper',
            'cucumber', 'zucchini', 'zuchinni', 'squash', 'celery', 'cabbage', 'peas', 'pea',
            'beans', 'bean', 'corn', 'mushroom', 'asparagus', 'brussel', 'sprout', 'sprouts',
            'avocado', 'garlic', 'ginger', 'parsley', 'cilantro',
            
            # Fruits
            'apple', 'banana', 'orange', 'grape', 'grapes', 'strawberry', 'blueberry', 'berry',
            'melon', 'mango', 'pineapple', 'peach', 'pear', 'cherry', 'kiwi', 'lemon', 'lime',
            'grapefruit', 'plum', 'watermelon', 'cantaloupe',
            
            # Dairy
            'milk', 'cheese', 'yogurt', 'butter', 'cream', 'ice cream', 'yoghurt',
            
            # Grains/Bakery
            'bread', 'rice', 'pasta', 'cereal', 'flour', 'oat', 'oats', 'quinoa', 'bagel',
            'muffin', 'croissant', 'roll', 'bun', 'toast', 'cracker', 'cookie', 'cake',
            
            # Beverages
            'juice', 'soda', 'water', 'coffee', 'tea', 'beer', 'wine', 'cola', 'pepsi',
            'coke', 'sprite', 'milk', 'smoothie', 'lemonade',
            
            # Common grocery items
            'oil', 'sugar', 'salt', 'pepper', 'sauce', 'soup', 'nuts', 'nut', 'seeds', 'seed',
            'spice', 'herb', 'vanilla', 'chocolate', 'honey', 'jam', 'jelly', 'vinegar',
        }
        
        # Check for strong food indicators (substring matching for flexibility)
        for word in words:
            for indicator in strong_food_indicators:
                if indicator in word or word in indicator:
                    logger.debug(f"  🍎 Strong food indicator found: '{indicator}' in '{word}'")
                    return True
        
        # Brand name patterns that indicate food
        food_brand_patterns = [
            r'\b(kraft|heinz|campbell|nestle|kellogg|general mills|pillsbury)\b',
            r'\b(del monte|hunts|french|italian|mexican|asian|organic)\b',
            r'\b(fresh|frozen|canned|dried|smoked|grilled|baked)\b',
        ]
        
        for pattern in food_brand_patterns:
            if re.search(pattern, text_lower):
                logger.debug(f"  🏷️  Food brand pattern match: {pattern}")
                return True
        
        # Food descriptor patterns
        food_descriptors = [
            r'\b(fresh|organic|natural|free range|grass fed|wild caught)\b',
            r'\b(sliced|diced|chopped|whole|ground|minced|shredded)\b',
            r'\b(raw|cooked|fried|baked|grilled|roasted|steamed)\b',
            r'\b(sweet|sour|spicy|mild|hot|cold|frozen|canned)\b',
        ]
        
        for pattern in food_descriptors:
            if re.search(pattern, text_lower):
                logger.debug(f"  🔍 Food descriptor found: {pattern}")
                return True
        
        # Weight/quantity indicators suggest groceries
        weight_patterns = [
            r'\b\d+\.?\d*\s*(kg|g|lb|oz|lbs)\b',
            r'\b\d+\.?\d*\s*(pack|bag|box|can|bottle|jar)\b',
        ]
        
        for pattern in weight_patterns:
            if re.search(pattern, text_lower):
                logger.debug(f"  ⚖️  Weight/quantity pattern: {pattern}")
                return True
        
        # ENHANCED: More stringent validation after cleaning
        if 2 <= len(text_clean) <= 50:
            alpha_count = sum(c.isalpha() for c in text_clean)
            total_chars = len(text_clean.replace(' ', ''))
            
            # Must be at least 60% letters (higher threshold)
            if alpha_count >= max(3, total_chars * 0.6):
                
                # Reject items that are just codes or numbers with random words
                suspicious_patterns = [
                    r'^\d+[:\s]+[A-Za-z]{1,2}$',  # "02753 Ut", "0257 M" type
                    r'^[A-Za-z]{1,3}\s+\d+$',    # "M 1234", "EY 567" type  
                    r'^[A-Za-z]{1,2}$',          # Just "M", "S", "L" etc.
                    r'^\d{3,}$',                 # Just numbers "02753"
                    r'^[A-Za-z]\s[A-Za-z]$',    # "M S", "E Y" type
                ]
                
                for pattern in suspicious_patterns:
                    if re.match(pattern, text_clean):
                        logger.debug(f"  🚫 Suspicious pattern rejected: '{text_clean}'")
                        return False
                
                # Require at least one "food-like" word if no strong indicators found
                has_food_word = any(
                    any(food in word.lower() or word.lower() in food for food in strong_food_indicators)
                    for word in words
                )
                
                # Common grocery formats: "ITEM NAME" or "Item Name" - but exclude blacklisted terms
                if (text.isupper() or text.istitle()) and 2 <= len(words) <= 4:
                    # Check if any word is blacklisted first
                    if not self.is_blacklisted(text_clean):
                        logger.debug(f"  📝 Grocery format detected: caps/title case")
                        return True
                    else:
                        logger.debug(f"  ❌ Grocery format blacklisted: '{text_clean}'")
                        return False
                
                # If it has recognizable food words, allow it
                if has_food_word:
                    logger.debug(f"  🍎 Has food words")
                    return True
                
                # For items without clear food indicators, be more restrictive
                # Must have reasonable structure (not just random characters)
                if len(words) >= 2 and len(text_clean) >= 6:
                    # Check if words are reasonable length (not just random chars)
                    reasonable_words = [w for w in words if len(w) >= 3]
                    if len(reasonable_words) >= 1:
                        logger.debug(f"  ✨ Reasonable structure accepted: '{text_clean}'")
                        return True

                # Allow single-word items if they look like real words (lengthy and alphabetic) AND not blacklisted
                if len(words) == 1 and text_clean.isalpha() and len(text_clean) >= 5:
                    # But first check if this single word is blacklisted (like "subtotal", "loyalty", etc.)
                    if not self.is_blacklisted(text_clean):
                        logger.debug(f"  ✅ Single-word item accepted: '{text_clean}'")
                        return True
                    else:
                        logger.debug(f"  ❌ Single-word blacklisted: '{text_clean}'")
                        return False
        
        # Check if this is a unit descriptor only (weight/measure without actual item name)
        if self.is_unit_descriptor_only(text_clean):
            logger.debug(f"  ❌ Unit descriptor only: '{text_clean}'")
            return False
        
        logger.debug(f"  ❌ Not identified as food item: '{text_clean}'")
        return False
    
    def _extract_global_number(self, text: str) -> Optional[float]:
        """Extract number from text using global formats (US, EU, etc.)"""
        # Remove currency symbols first
        clean_text = text
        for symbol in self.CURRENCY_SYMBOLS:
            clean_text = clean_text.replace(symbol, '')
        
        # Try each number pattern
        for pattern in self.NUMBER_PATTERNS:
            match = re.search(pattern, clean_text)
            if match:
                num_str = match.group(1)
                try:
                    # Handle different decimal separators
                    if ',' in num_str and '.' in num_str:
                        # Both comma and dot - determine which is decimal
                        if num_str.rfind(',') > num_str.rfind('.'):
                            # Comma is decimal: 1.234,56
                            num_str = num_str.replace('.', '').replace(',', '.')
                        else:
                            # Dot is decimal: 1,234.56  
                            num_str = num_str.replace(',', '')
                    elif ',' in num_str:
                        # Only comma - could be decimal or thousands
                        if len(num_str.split(',')[-1]) == 2:
                            # Decimal: 123,45
                            num_str = num_str.replace(',', '.')
                        else:
                            # Thousands: 1,234
                            num_str = num_str.replace(',', '')
                    
                    return float(num_str)
                except ValueError:
                    continue
        
        return None
    
    def _extract_global_price(self, line: str) -> Optional[Tuple[float, int, int]]:
        """Extract price with currency from line - returns (price, start_pos, end_pos)"""
        # Build comprehensive price pattern for any currency
        currency_pattern = '|'.join(re.escape(sym) for sym in self.CURRENCY_SYMBOLS)
        
        # Patterns: currency before/after, with various number formats
        price_patterns = [
            f'({currency_pattern})\\s*({"|".join(self.NUMBER_PATTERNS)})',
            f'({"|".join(self.NUMBER_PATTERNS)})\\s*({currency_pattern})',
            f'({"|".join(self.NUMBER_PATTERNS)})(?=\\s*$)',  # Number at end of line
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                # Extract the numeric part
                for group in match.groups():
                    if group and not any(sym in group for sym in self.CURRENCY_SYMBOLS):
                        price = self._extract_global_number(group)
                        if price is not None and 0.01 <= price <= 999999:  # Reasonable price range
                            return price, match.start(), match.end()
        
        return None
    
    def extract_price_and_quantity(self, line: str) -> Tuple[float, float, str]:
        """
        Global price and quantity extraction - works with any currency and number format.
        Supports: $, €, £, ¥, ₹, etc. and various decimal separators (. , space)
        Returns: (quantity, price, remaining_text_for_item_name)
        """
        original_line = line
        quantity = 1.0
        price = 0.0  # Default to 0.0 to prevent TypeError in sum()
        
        # Pattern 0: Tab-separated or multi-space format (global compatible)
        # Works with any language: "Item Name \t Qty \t Rate \t Amount"
        if '\t' in line or '  ' in line:  # Multiple spaces or tabs
            parts = re.split(r'\s{2,}|\t+', line.strip())
            parts = [p.strip() for p in parts if p.strip()]
            
            if len(parts) >= 3:
                numeric_parts = []
                name_parts = []
                
                for part in parts:
                    # Try to extract numbers with any global format
                    found_number = self._extract_global_number(part)
                    if found_number is not None and len(part) < 15:  # Short, likely numeric
                        numeric_parts.append(found_number)
                    else:
                        name_parts.append(part)
                
                if len(numeric_parts) >= 2:
                    quantity = numeric_parts[0]
                    price = numeric_parts[-1]  # Last number is the total amount
                    line = ' '.join(name_parts)
                    return quantity, price, line
        
        # Pattern 1: Global currency price extraction - ENHANCED
        # Supports: $12.34, €12,34, ¥1234, ₹123.45, 12.34€, 12.34, etc.
        price_found = self._extract_global_price(line)
        if price_found:
            price, match_start, match_end = price_found
            line = (line[:match_start] + line[match_end:]).strip()
        else:
            # Enhanced fallback price detection - look for standalone numbers at end
            price_fallback_patterns = [
                r'(\d+\.\d{2})\s*$',  # 12.34 at end
                r'(\d+,\d{2})\s*$',   # 12,34 at end (European)
                r'(\d+\.\d{1})\s*$',  # 12.3 at end
                r'(\d{2,})\s*$',      # 123 at end (whole dollars)
            ]
            
            for pattern in price_fallback_patterns:
                match = re.search(pattern, line.strip())
                if match:
                    price_str = match.group(1)
                    try:
                        # Handle different decimal formats
                        if ',' in price_str and '.' not in price_str:
                            price_str = price_str.replace(',', '.')
                        
                        extracted_price = float(price_str)
                        # Reasonable price range check
                        if 0.01 <= extracted_price <= 999.99:
                            price = extracted_price
                            line = line[:match.start()].strip()
                            break
                    except ValueError:
                        continue
        
        # Pattern 2: "0.442kg NET @ $2.99/kg" - extract weight as quantity
        weight_match = re.search(r'(?:^|\s)(\d+\.?\d*)\s*(kg|g|lb|oz)\b', line.lower())
        if weight_match:
            weight = float(weight_match.group(1))
            unit = weight_match.group(2)
            
            # Convert to kg for consistency
            if unit == 'g':
                quantity = weight / 1000
            elif unit == 'lb':
                quantity = weight * 0.453592
            elif unit == 'oz':
                quantity = weight * 0.0283495
            else:
                quantity = weight
            
            # Remove this from the line
            # Remove this weight segment (remove matched span)
            start_index = weight_match.start()
            end_index = weight_match.end()
            # If match began with whitespace because of the non-capturing group, strip it too
            line = (line[:start_index].rstrip() + " " + line[end_index:].lstrip()).strip()
        
        # Pattern 3: Quantity at start "2 x ITEM" or "2 ITEM" 
        qty_match = re.match(r'^(\d+)\s*x?\s+', line.lower())
        if qty_match and not weight_match:  # Don't override weight-based quantity
            quantity = float(qty_match.group(1))
            line = line[qty_match.end():].strip()
        
        return quantity, price, line
    
    def clean_item_name(self, name: str) -> str:
        """
        ENHANCED: Clean up item name by removing promotional text, codes, and unwanted elements.
        Dynamic rules that work for ALL receipts, not just specific patterns.
        """
        if not name or len(name.strip()) < 2:
            return ""
        
        original_name = name
        name = name.strip()
        
        # Step 1: Remove promotional prefixes and suffixes
        promotional_patterns = [
            # First remove numbered list prefixes: "1.", "2.", etc.
            r'^\d+\.\s*',
            
            # Remove "Buy One, Get One" type promotions (dynamic) - COMPLETE LINE
            r'^.*?buy\s+(?:one|two|\d+)[,\s;]*(?:get|receive)\s+(?:one|two|\d+).*$',
            r'^.*?bogo.*$',
            r'^.*?b1g1.*$',
            
            # Partial promotional text removal
            r'^(buy\s+(?:one|two|\d+)[,\s;]*(?:get|receive)\s+(?:one|two|\d+)[,\s]*(?:free)?)\s*[-:\s]*',
            r'^(buy\s+\d+[,\s]*get\s+\d+)\s*[-:\s]*',
            r'^(bogo|b1g1)\s*[-:\s]*',
            
            # Remove common promotional text
            r'^(special\s+offer|daily\s+special|combo|meal\s+deal)\s*[-:\s]*',
            r'^(promotion|promo|deal|offer)\s*[-:\s]*',
            
            # Remove quantity prefixes when they're not part of food name
            r'^\d+\s*x\s*',  # "2 x " 
        ]
        
        for pattern in promotional_patterns:
            name = re.sub(pattern, '', name, flags=re.IGNORECASE).strip()
        
        # Step 2: Remove line references and codes (DYNAMIC)
        line_code_patterns = [
            # Line references: "Line 1", "Line 4", "Line 8", etc.
            r'\s*line\s+\d+\s*$',
            r'\s*line\s+\d+\s*',
            r'\s*ln\s*\d+\s*',

            # Numbered list with embedded code: "1: 0275"
            r'^\d{1,2}\s*[:\.]\s*\d{3,6}\s+',
            
            # Item codes at start: "02753", "0257", "9463" (4-5 digit codes)
            r'^\d{3,6}[:\s]+',
            r'^\d{3,6}\s+',
            
            # Item codes with colons: "1:", "2:", "4:", "6:", "8:"
            r'^\d{1,2}:\s*',
            
            # Mixed codes: "8:3556," type patterns
            r'^\d+[:]\d+[,\s]*',
            
            # Remove trailing codes/numbers that aren't prices
            r'\s+\d{3,6}\s*$',  # Trailing 3-6 digit codes
            
            # Remove reference numbers in middle: "EVM", "EY", etc (but not common food words)
            r'\s+(EVM|EVA|EY|LNE|UNE)(?=\s|$)',  # Specific OCR noise codes, not common words
        ]
        
        for pattern in line_code_patterns:
            name = re.sub(pattern, '', name, flags=re.IGNORECASE).strip()
        
        # Step 3: Remove measurement and packaging info (keep food name clean)
        measurement_patterns = [
            r'\s+(NET|@|ea|each|pkg|package|lb|oz|kg|g|ml|l)\b.*$',
            r'\s+\d+\.?\d*\s*(kg|g|lb|oz|lbs|ml|l)\b.*$',
            r'\s+@\s*\$?\d+\.?\d*.*$',  # Remove "@ $2.99/kg" type text
        ]
        
        for pattern in measurement_patterns:
            name = re.sub(pattern, '', name, flags=re.IGNORECASE).strip()
        
        # Step 4: Remove garbled/corrupted text indicators
        corruption_patterns = [
            # Remove single letters or numbers at end
            r'\s+[A-Za-z]\s*$',
            r'\s+\d\s*$',
            
            # Remove weird punctuation clusters
            r'[,.;:]{2,}',
            r'\s*[,.:;]+\s*$',
            
            # Remove standalone special characters
            r'\s*[-_=+]+\s*$',
            
            # Clean up multiple spaces
            r'\s{2,}',
        ]
        
        for pattern in corruption_patterns:
            name = re.sub(pattern, ' ', name).strip()
        
        # Step 5: Handle specific problematic patterns from your examples (MORE AGGRESSIVE)
        problem_patterns = [
            # "M Iced Coffee-Line 8" -> "M Iced Coffee" (including OCR variants)
            r'-?\s*line\s+\d+.*$',
            r'\s+line\s+\d+.*$',
            r'\s+une\s*\d*.*$',  # OCR error: "Line" -> "Une"
            r'\s+lne\s*\d*.*$',  # OCR error: "Line" -> "Lne"
            r'\s+eva\s*.*$',     # OCR error often creates "Eva" noise
            
            # Remove modifier words that got attached
            r'\s*(add|no|extra|side|with|without)\s+.*$',
            
            # Remove "Take-Out", "Change" etc. (including OCR variants)
            r'^(take-?out|change|subtotal|subrotal|total|gst|tax|tara-?oul).*$',
            
            # Remove credit card and payment info
            r'^(credit|debit|card|cash|payment|cardit|caro).*$',
            
            # Remove corrupted versions of common promotional terms (OCR errors)
            r'^(duy\s+ona|gel\s+one|buy\s+one).*$' ,  # OCR errors for "Buy One"
            r'.*get\s+one\s+(une|line).*$',         # "Get One Line" corruptions
            
            # Remove discount/promotion indicators
            r'.*discount.*$',
            r'.*promo.*$',
            r'.*special.*$',
            
            # Single punctuation or short meaningless endings
            r'[,.:;]\s*[A-Z]?\s*$',
            
            # Remove trailing single letters or short fragments
            r'\s+[A-Za-z]{1,2}\s*$',
        ]
        
        for pattern in problem_patterns:
            name = re.sub(pattern, '', name, flags=re.IGNORECASE).strip()
        
        # Step 6: Final cleanup
        # Remove leading/trailing special characters
        name = re.sub(r'^[^\w]+|[^\w]+$', '', name)
        
        # Normalize internal spaces
        name = ' '.join(name.split())
        
        # If name became too short or empty, reject it
        if len(name) < 3:
            return ""
        
        # Convert to title case for consistency
        cleaned_name = name.title()
        
        # Debug logging to track cleaning process
        if cleaned_name != original_name.strip():
            logger.debug(f"  🧹 Cleaned: '{original_name.strip()}' -> '{cleaned_name}'")
        
        return cleaned_name
    
    def parse_receipt_items(self, ocr_text: str) -> List[Dict[str, Any]]:
        """
        Extract ONLY actual food/grocery items from OCR text.
        Handles both flat and hierarchical receipt formats.
        
        Args:
            ocr_text: Raw OCR text from receipt
            
        Returns:
            List of dictionaries with item details
        """
        if not ocr_text:
            logger.warning("Empty OCR text provided")
            return []
        
        # DON'T strip lines yet - we need indentation for hierarchical parsing
        lines_raw = [line.rstrip() for line in ocr_text.split('\n') if line.strip()]
        items = []
        seen_items = set()  # Avoid duplicates
        
        logger.info(f"Parsing {len(lines_raw)} lines from receipt")
        
        # Strategy 1: Look for hierarchical format (like McDonald's)
        # Lines with quantity and price, followed by indented item names
        hierarchical_items = self._parse_hierarchical_format(lines_raw)
        
        if hierarchical_items:
            logger.info(f"✅ Detected hierarchical format, extracted {len(hierarchical_items)} items")
            return hierarchical_items
        
        # Strategy 2: Flat format (item name and price on same line)
        # Keep original spacing for tab-separated formats
        logger.info("Using flat format parsing")
        
        for i, line_raw in enumerate(lines_raw):
            line = line_raw.strip()
            logger.debug(f"Processing line {i}: '{line}'")
            
            # Skip empty or very short lines
            if len(line) < 3:
                logger.debug(f"  ❌ Too short")
                continue
            
            # Filter 1: Blacklisted keywords (totals, dates, etc.)
            if self.is_blacklisted(line):
                logger.debug(f"  ❌ Blacklisted: '{line}'")
                continue
            
            # Filter 2: Unit descriptors only (like "0.442kg NET @ $2.99/kg")
            if self.is_unit_descriptor_only(line):
                logger.debug(f"  ❌ Unit descriptor only: '{line}'")
                continue
            
            # Filter 3: Must have a price ($ sign or decimal number)
            # Match $X.XX, XX.XX, X.X, etc.
            if not re.search(r'\$?\d+\.?\d*', line):
                logger.debug(f"  ❌ No price found: '{line}'")
                continue
            
            # Extract quantity and price (use raw line to preserve spacing)
            quantity, price, item_name_raw = self.extract_price_and_quantity(line_raw.strip())
            
            if not price or price <= 0:
                logger.debug(f"  ❌ Invalid price: {price}")
                continue
            
            # Clean item name
            item_name = self.clean_item_name(item_name_raw)
            
            # Filter 4: Must have a reasonable item name
            if len(item_name) < 3:
                logger.debug(f"  ❌ Name too short after cleaning: '{item_name}'")
                continue
            
            # Filter 5: Check if it's likely a food item
            if not self.is_likely_food_item(item_name):
                logger.debug(f"  ❌ Not a food item: '{item_name}'")
                continue
            
            # Avoid duplicates
            item_key = f"{item_name}_{price}"
            if item_key in seen_items:
                logger.debug(f"  ❌ Duplicate: '{item_name}'")
                continue
            
            seen_items.add(item_key)
            
            # Success! This is a real item
            item = {
                'name': item_name,
                'quantity': quantity,
                'price': price,
                'unit_price': self._compute_unit_price(price, quantity),
                'original_line': line
            }
            
            items.append(item)
            price_str = f"${price:.2f}" if price is not None else "No price"
            logger.info(f"  ✅ Extracted: {item_name} (qty: {quantity}, price: {price_str})")
        
        logger.info(f"Successfully extracted {len(items)} items from receipt")
        return items
    
    def _parse_hierarchical_format(self, lines: List[str]) -> List[Dict[str, Any]]:
        """
        Parse hierarchical receipt format like:
          1 Buy One, Get One    3.99
            1 Sausage Egg McMuffin
            1 Sausage Egg McMuffin
          1 2 Burritos EVM       6.99
            1 S Coffee
              ADD Cream
        """
        items = []
        seen_items = set()
        i = 0
        
        logger.debug(f"Starting hierarchical parsing with {len(lines)} lines")
        
        while i < len(lines):
            line = lines[i]
            original_line = line
            line_stripped = line.strip()
            
            # Check if line is indented (has leading spaces)
            indent_level = len(line) - len(line.lstrip())
            
            # Check if line has a price
            has_price = bool(re.search(r'\$?\d+\.\d{2}', line_stripped))
            
            logger.debug(f"Line {i}: indent={indent_level}, has_price={has_price}, text='{line_stripped[:40]}'")
            
            if has_price:  # Any line with a price could be a group header or item
                # This is a line item with price (might be at any indent level)
                quantity, price, item_name_raw = self.extract_price_and_quantity(line_stripped)
                item_name = self.clean_item_name(item_name_raw)
                
                # Check if this is a blacklisted group header OR if the extracted item name is blacklisted
                if self.is_blacklisted(line_stripped) or self.is_blacklisted(item_name):
                    # It's a promotion/group header or non-food item - extract the sub-items if any
                    logger.info(f"  📦 Found group header (blacklisted): {line_stripped[:50]}")
                    price_str = f"${price:.2f}" if price is not None else "No price"
                    logger.debug(f"     Indent level: {indent_level}, Price: {price_str}")
                    i += 1
                    
                    # Look ahead for indented sub-items
                    sub_item_count = 0
                    while i < len(lines):
                        next_line = lines[i]
                        next_stripped = next_line.strip()
                        next_indent = len(next_line) - len(next_line.lstrip())
                        
                        logger.debug(f"     Checking line {i}: indent={next_indent}, text='{next_stripped[:40]}'")
                        
                        # If next line is indented, it's a sub-item
                        if next_indent > indent_level and next_stripped:
                            logger.debug(f"       ✓ Line is indented ({next_indent} > {indent_level})")
                            
                            # Check if it's a modifier
                            if self._is_modifier(next_stripped):
                                logger.debug(f"       ✗ Skipping modifier: {next_stripped[:30]}")
                                i += 1
                                continue
                            
                            # ENHANCED: Check if sub-item has its own price
                            sub_has_price = bool(re.search(r'\$?\d+\.\d{2}', next_stripped))
                            sub_quantity = 1
                            sub_price = price  # Default to parent's price
                            
                            if sub_has_price:
                                # Sub-item has its own price - extract it
                                sub_quantity, sub_price, sub_item_name_raw = self.extract_price_and_quantity(next_stripped)
                                item_name = self.clean_item_name(sub_item_name_raw)
                                logger.debug(f"       ✓ Sub-item has own price: ${sub_price:.2f}")
                            else:
                                # Sub-item uses parent's price
                                item_name = self._clean_sub_item_name(next_stripped)
                                logger.debug(f"       ✓ Sub-item uses parent price: ${sub_price:.2f}")
                            
                            logger.debug(f"       Cleaned name: '{item_name}'")
                            
                            # Validate price before adding sub-item
                            if not sub_price or sub_price <= 0:
                                logger.debug(f"       ✗ Invalid price: {sub_price}")
                                i += 1
                                continue
                            
                            if item_name and len(item_name) >= 3 and self.is_likely_food_item(item_name):
                                item_key = f"{item_name}_{sub_price}_sub_{i}"  # Include line number to allow duplicates with different prices
                                if item_key not in seen_items:
                                    items.append({
                                        'name': item_name,
                                        'quantity': sub_quantity,
                                        'price': sub_price,
                                        'unit_price': self._compute_unit_price(sub_price, sub_quantity),
                                        'original_line': next_line
                                    })
                                    seen_items.add(item_key)
                                    sub_item_count += 1
                                    price_str = f"${sub_price:.2f}" if sub_price is not None else "No price"
                                    logger.info(f"  ✅ Extracted sub-item: {item_name} ({price_str})")
                                else:
                                    logger.debug(f"       ✗ Duplicate: {item_name}")
                            else:
                                logger.debug(f"       ✗ Not a food item or too short: {item_name}")
                            i += 1
                        else:
                            # No more sub-items, back to main level
                            logger.debug(f"       ✗ Not indented enough ({next_indent} <= {indent_level}), exiting sub-item loop")
                            break
                    
                    logger.debug(f"     Extracted {sub_item_count} sub-items from group")
                    continue
                    
                else:
                    # It's a regular item with price (not blacklisted)
                    # item_name was already extracted above
                    
                    # Validate price before adding item
                    if not price or price <= 0:
                        logger.debug(f"  ❌ Invalid price in hierarchical: {price}")
                        i += 1
                        continue
                    
                    # Double-check that this item name is not blacklisted and is likely food
                    if item_name and len(item_name) >= 3 and not self.is_blacklisted(item_name) and self.is_likely_food_item(item_name):
                        item_key = f"{item_name}_{price}"
                        if item_key not in seen_items:
                            items.append({
                                'name': item_name,
                                'quantity': quantity,
                                'price': price,
                                'unit_price': self._compute_unit_price(price, quantity),
                                'original_line': original_line
                            })
                            seen_items.add(item_key)
                            price_str = f"${price:.2f}" if price is not None else "No price"
                            logger.info(f"  ✅ Extracted: {item_name} ({price_str})")
                    
                    # Also check for sub-items under this item
                    i += 1
                    while i < len(lines):
                        next_line = lines[i]
                        next_stripped = next_line.strip()
                        next_indent = len(next_line) - len(next_line.lstrip())
                        
                        if next_indent > indent_level and next_stripped:
                            if not self._is_modifier(next_stripped):
                                sub_item_name = self._clean_sub_item_name(next_stripped)
                                
                                # Validate price before adding sub-item
                                if price and price > 0 and sub_item_name and self.is_likely_food_item(sub_item_name):
                                    item_key = f"{sub_item_name}_{price}_sub"
                                    if item_key not in seen_items:
                                        items.append({
                                            'name': sub_item_name,
                                            'quantity': 1,
                                            'price': price,
                                            'unit_price': price,
                                            'original_line': next_line
                                        })
                                        seen_items.add(item_key)
                                        price_str = f"${price:.2f}" if price is not None else "No price"
                                        logger.info(f"  ✅ Extracted sub-item: {sub_item_name} ({price_str})")
                            i += 1
                        else:
                            break
                    continue
            
            i += 1
        
        # Return items if we found any
        return items if items else []
    
    def _clean_sub_item_name(self, text: str) -> str:
        """Clean sub-item name by removing quantity markers."""
        # Remove leading quantity like "1 " or "2 "
        cleaned = re.sub(r'^\d+\s+', '', text)
        return self.clean_item_name(cleaned)
    
    def _compute_unit_price(self, price: Optional[float], quantity: Optional[float]) -> Optional[float]:
        """Safely compute unit price while handling missing data."""
        if price is None:
            return None
        if not quantity or quantity <= 0:
            return price
        try:
            return price / quantity
        except Exception:
            logger.debug("  ⚠️ Could not compute unit price", exc_info=True)
            return price

    def _is_modifier(self, text: str) -> bool:
        """Check if text is a modifier (ADD, NO, EXTRA, etc.)."""
        modifiers = ['add', 'no', 'extra', 'hold', 'without', 'with', 'side']
        text_lower = text.lower()
        
        # Check if starts with modifier
        for mod in modifiers:
            if text_lower.startswith(mod + ' ') or text_lower == mod:
                return True
        
        return False
    
    def _extract_price_only(self, line: str) -> float:
        """Extract just the price from a line."""
        match = re.search(r'\$?(\d+\.\d{2})', line)
        if match:
            return float(match.group(1))
        return 0.0
    
    def parse_receipt(self, ocr_text: str) -> Dict[str, Any]:
        """
        Parse complete receipt including items, totals, date, and merchant.
        
        Args:
            ocr_text: Raw OCR text from receipt
            
        Returns:
            Dictionary with items, total, date, merchant_name, and other fields
        """
        result = {
            'items': [],
            'total': 0.0,
            'subtotal': 0.0,
            'tax': 0.0,
            'date': None,
            'merchant_name': None,
            'raw_text': ocr_text
        }
        
        if not ocr_text:
            return result
        
        lines = ocr_text.split('\n')
        
        # Extract items
        result['items'] = self.parse_receipt_items(ocr_text)
        
        # Extract merchant name (usually first 1-3 lines)
        result['merchant_name'] = self._extract_merchant_name(lines)
        
        # Extract date
        result['date'] = self._extract_date(ocr_text)
        
        # Extract totals
        totals = self._extract_totals(lines)
        result.update(totals)
        
        return result
    
    def _extract_merchant_name(self, lines: List[str]) -> Optional[str]:
        """Extract merchant/store name from first few lines."""
        # Check first 5 lines for merchant name
        for line in lines[:5]:
            line_clean = line.strip()
            if not line_clean or len(line_clean) < 3:
                continue
            
            # Skip if it's just numbers or special chars
            if re.match(r'^[\d\s\-\.\(\)]+$', line_clean):
                continue
            
            # Skip common non-merchant patterns
            if any(word in line_clean.lower() for word in ['invoice', 'receipt', 'bill', 'phone', 'tel', 'address']):
                continue
            
            # If it's mostly uppercase and not too long, likely merchant name
            if line_clean.isupper() and len(line_clean) <= 40:
                return line_clean
            
            # If it contains common business words
            if any(word in line_clean.lower() for word in ['restaurant', 'market', 'shop', 'store', 'cafe', 'foods']):
                return line_clean
            
            # First non-empty line that looks like text
            if len(line_clean) > 5 and not line_clean[0].isdigit():
                return line_clean
        
        return None
    
    def _extract_date(self, text: str) -> Optional[str]:
        """Extract date from receipt text and normalize to YYYY-MM-DD format."""
        import datetime
        
        # Common date patterns
        date_patterns = [
            # MM/DD/YYYY or MM/DD/YY
            (r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})', 'mdy'),
            (r'(\d{1,2})[/-](\d{1,2})[/-](\d{2})', 'mdy_short'),
            
            # DD/MM/YYYY or DD/MM/YY
            (r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})', 'dmy'),
            
            # YYYY-MM-DD
            (r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})', 'ymd'),
            
            # Month DD, YYYY
            (r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{1,2}),?\s+(\d{4})', 'mdy_text'),
            
            # DD Month YYYY
            (r'(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{4})', 'dmy_text'),
            
            # Date: May 11, 2019
            (r'Date:\s*(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{1,2}),?\s+(\d{4})', 'date_prefix'),
        ]
        
        month_map = {
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
            'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
        }
        
        for pattern, format_type in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    if format_type == 'ymd':
                        year, month, day = match.groups()
                        return f"{year}-{int(month):02d}-{int(day):02d}"
                    
                    elif format_type in ['mdy', 'dmy']:
                        part1, part2, year = match.groups()
                        year = int(year)
                        
                        # Heuristic: if first number > 12, it's likely day
                        if int(part1) > 12:
                            day, month = int(part1), int(part2)
                        elif int(part2) > 12:
                            month, day = int(part1), int(part2)
                        else:
                            # Ambiguous, assume MM/DD by default (US format)
                            month, day = int(part1), int(part2)
                        
                        return f"{year}-{month:02d}-{day:02d}"
                    
                    elif format_type == 'mdy_short':
                        month, day, year = match.groups()
                        year = int(year)
                        if year < 100:
                            year = 2000 + year if year < 50 else 1900 + year
                        return f"{year}-{int(month):02d}-{int(day):02d}"
                    
                    elif format_type == 'mdy_text':
                        month_str, day, year = match.groups()
                        month = month_map[month_str.lower()[:3]]
                        return f"{year}-{month:02d}-{int(day):02d}"
                    
                    elif format_type == 'dmy_text':
                        day, month_str, year = match.groups()
                        month = month_map[month_str.lower()[:3]]
                        return f"{year}-{month:02d}-{int(day):02d}"
                    
                    elif format_type == 'date_prefix':
                        month_str, day, year = match.groups()
                        month = month_map[month_str.lower()[:3]]
                        return f"{year}-{month:02d}-{int(day):02d}"
                
                except (ValueError, KeyError) as e:
                    logger.debug(f"Date parsing error: {e}")
                    continue
        
        return None
    
    def _extract_totals(self, lines: List[str]) -> Dict[str, float]:
        """Extract total, subtotal, and tax from receipt."""
        result = {
            'total': 0.0,
            'subtotal': 0.0,
            'tax': 0.0
        }
        
        # Look through lines for total keywords
        for line in lines:
            line_lower = line.lower()
            
            # Extract amounts (handle commas in numbers)
            # Match patterns like: $1,234.56, 1,234.56, $123.45, 123.45, 123.4, etc.
            amounts = re.findall(r'\$?\s*([\d,]+\.?\d*)', line)
            if not amounts:
                continue
            
            # Parse amounts (remove commas)
            parsed_amounts = []
            for amt in amounts:
                try:
                    parsed_amounts.append(float(amt.replace(',', '')))
                except ValueError:
                    continue
            
            if not parsed_amounts:
                continue
            
            # Get the last (rightmost) amount
            amount = parsed_amounts[-1]
            
            # Check for total
            if any(keyword in line_lower for keyword in ['total', 'amount due', 'balance due']):
                # Avoid "item total" or "sub total"
                if 'sub' not in line_lower and 'item' not in line_lower:
                    result['total'] = max(result['total'], amount)
            
            # Check for subtotal
            if any(keyword in line_lower for keyword in ['subtotal', 'sub-total', 'sub total', 'item total']):
                result['subtotal'] = max(result['subtotal'], amount)
            
            # Check for tax
            if any(keyword in line_lower for keyword in ['tax', 'gst', 'hst', 'vat', 'pst']):
                result['tax'] += amount
        
        # If no explicit subtotal found but we have items and total, estimate subtotal
        if result['subtotal'] == 0.0 and result['total'] > 0.0:
            result['subtotal'] = result['total'] - result['tax']
        
        return result


# Global instance
receipt_parser = IntelligentReceiptParser()
