"""
Lightweight Food Classifier - Works without heavy ML models
Uses color analysis and image features for food detection
"""

import io
import logging
from typing import Dict, List, Any
from PIL import Image
import colorsys
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LightweightFoodClassifier:
    """Lightweight food classification using color and image analysis."""
    
    def __init__(self):
        logger.info("Initializing Lightweight Food Classifier...")
        
        # Food database with color profiles and nutritional info
        self.food_database = {
            'banana': {
                'color_ranges': [(40, 70), (200, 255), (100, 200)],  # HSL: Yellow hue, high lightness
                'category': 'fruits',
                'display_name': 'Banana',
                'calories': 89,
                'protein': 1.1,
                'carbohydrates': 22.8,
                'fat': 0.3,
                'fiber': 2.6,
                'key_nutrients': ['potassium', 'vitamin B6', 'vitamin C'],
                'portion_size': 100,  # grams
                'portion_description': '1 medium banana (about 7-8 inches)'
            },
            'apple': {
                'color_ranges': [(0, 15), (50, 200), (80, 180)],  # Red hue
                'category': 'fruits',
                'display_name': 'Apple',
                'calories': 52,
                'protein': 0.3,
                'carbohydrates': 13.8,
                'fat': 0.2,
                'fiber': 2.4,
                'key_nutrients': ['vitamin C', 'fiber', 'antioxidants'],
                'portion_size': 100,
                'portion_description': '1 medium apple'
            },
            'orange': {
                'color_ranges': [(20, 40), (150, 255), (120, 200)],  # Orange hue
                'category': 'fruits',
                'display_name': 'Orange',
                'calories': 47,
                'protein': 0.9,
                'carbohydrates': 11.8,
                'fat': 0.1,
                'fiber': 2.4,
                'key_nutrients': ['vitamin C', 'folate', 'thiamine'],
                'portion_size': 100,
                'portion_description': '1 medium orange'
            },
            'broccoli': {
                'color_ranges': [(80, 140), (50, 180), (50, 120)],  # Green hue
                'category': 'vegetables',
                'display_name': 'Broccoli',
                'calories': 34,
                'protein': 2.8,
                'carbohydrates': 6.6,
                'fat': 0.4,
                'fiber': 2.6,
                'key_nutrients': ['vitamin C', 'vitamin K', 'folate'],
                'portion_size': 100,
                'portion_description': '1 cup chopped'
            },
            'tomato': {
                'color_ranges': [(0, 15), (100, 200), (100, 180)],  # Red hue
                'category': 'vegetables',
                'display_name': 'Tomato',
                'calories': 18,
                'protein': 0.9,
                'carbohydrates': 3.9,
                'fat': 0.2,
                'fiber': 1.2,
                'key_nutrients': ['vitamin C', 'lycopene', 'vitamin K'],
                'portion_size': 100,
                'portion_description': '1 medium tomato'
            }
        }
        
        logger.info(f"✅ Lightweight classifier initialized with {len(self.food_database)} food items")
    
    def analyze_color(self, image: Image.Image) -> Dict[str, float]:
        """Analyze dominant colors in the image."""
        # Resize for faster processing
        img = image.copy()
        img.thumbnail((150, 150))
        
        # Convert to RGB
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Get pixel data
        pixels = list(img.getdata())
        
        # Calculate average color
        avg_r = sum(p[0] for p in pixels) / len(pixels)
        avg_g = sum(p[1] for p in pixels) / len(pixels)
        avg_b = sum(p[2] for p in pixels) / len(pixels)
        
        # Convert to HSL
        h, l, s = colorsys.rgb_to_hls(avg_r/255, avg_g/255, avg_b/255)
        h_deg = h * 360  # Convert to degrees
        s_pct = s * 255
        l_pct = l * 255
        
        return {
            'hue': h_deg,
            'saturation': s_pct,
            'lightness': l_pct,
            'rgb': (avg_r, avg_g, avg_b)
        }
    
    def match_food_by_color(self, color_analysis: Dict[str, float]) -> List[Dict[str, Any]]:
        """Match food items based on color analysis."""
        matches = []
        
        h = color_analysis['hue']
        s = color_analysis['saturation']
        l = color_analysis['lightness']
        
        for food_name, food_data in self.food_database.items():
            color_range = food_data['color_ranges']
            h_range, l_range, s_range = color_range
            
            # Check if color falls within ranges
            h_match = h_range[0] <= h <= h_range[1]
            l_match = l_range[0] <= l <= l_range[1]
            s_match = s_range[0] <= s <= s_range[1]
            
            # Calculate confidence based on how well it matches
            confidence = 0.0
            if h_match:
                confidence += 0.4
            if l_match:
                confidence += 0.3
            if s_match:
                confidence += 0.3
            
            if confidence > 0.3:  # Threshold for including in results
                matches.append({
                    'food_name': food_name,
                    'confidence': confidence,
                    'food_data': food_data
                })
        
        # Sort by confidence
        matches.sort(key=lambda x: x['confidence'], reverse=True)
        return matches
    
    def classify_food(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Classify food from image bytes.
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            Classification result dictionary
        """
        try:
            # Load image
            image = Image.open(io.BytesIO(image_bytes))
            
            # Analyze color
            color_analysis = self.analyze_color(image)
            logger.info(f"Color analysis: Hue={color_analysis['hue']:.1f}, Sat={color_analysis['saturation']:.1f}, Light={color_analysis['lightness']:.1f}")
            
            # Match foods
            matches = self.match_food_by_color(color_analysis)
            
            if not matches:
                return {
                    'success': False,
                    'error': 'No matching food items found',
                    'ingredients': [],
                    'confidence': 0.0
                }
            
            # Format ingredients
            ingredients = []
            detailed_breakdown = []
            total_calories = 0
            total_protein = 0
            total_carbs = 0
            total_fat = 0
            total_fiber = 0
            total_weight = 0
            
            for match in matches[:5]:  # Top 5 matches
                food_name = match['food_name']
                food_data = match['food_data']
                confidence = match['confidence']
                
                ingredient = {
                    'name': food_data['display_name'],
                    'confidence': confidence,
                    'category': food_data['category'],
                    'nutritional_info': {
                        'calories': food_data['calories'],
                        'protein': food_data['protein'],
                        'carbohydrates': food_data['carbohydrates'],
                        'fat': food_data['fat'],
                        'fiber': food_data['fiber'],
                        'portion_size_g': food_data['portion_size'],
                        'portion_description': food_data['portion_description']
                    },
                    'key_nutrients': food_data['key_nutrients']
                }
                ingredients.append(ingredient)
                
                # Build detailed breakdown for calorie analysis
                breakdown_item = {
                    'name': food_data['display_name'],
                    'portion_size_g': food_data['portion_size'],
                    'calories': food_data['calories'],
                    'protein': food_data['protein'],
                    'carbs': food_data['carbohydrates'],
                    'fat': food_data['fat'],
                    'fiber': food_data['fiber'],
                    'confidence': confidence
                }
                detailed_breakdown.append(breakdown_item)
                
                # Accumulate totals (only for top match)
                if len(detailed_breakdown) == 1:
                    total_calories = food_data['calories']
                    total_protein = food_data['protein']
                    total_carbs = food_data['carbohydrates']
                    total_fat = food_data['fat']
                    total_fiber = food_data['fiber']
                    total_weight = food_data['portion_size']
            
            # Calculate nutritional percentages
            total_macros = total_protein + total_carbs + total_fat
            protein_pct = (total_protein * 4 / (total_macros * 4)) * 100 if total_macros > 0 else 0
            fat_pct = (total_fat * 9 / (total_macros * 4 + total_fat * 5)) * 100 if total_macros > 0 else 0
            
            # Calculate quality score (simple heuristic)
            quality_score = min(100, (
                (total_fiber * 10) +  # Fiber is good
                (total_protein * 2) +  # Protein is good
                max(0, 50 - total_fat * 5)  # Too much fat is bad
            ))
            
            quality_rating = "excellent" if quality_score >= 80 else "good" if quality_score >= 60 else "fair" if quality_score >= 40 else "poor"
            
            return {
                'success': True,
                'confidence': matches[0]['confidence'],
                'ingredients': ingredients,
                'total_ingredients': len(ingredients),
                'processing_time': datetime.now().isoformat(),
                'color_analysis': color_analysis,
                'nutritional_analysis': {
                    'total_ingredients': len(ingredients),
                    'average_confidence': sum(m['confidence'] for m in matches[:5]) / len(matches[:5]),
                    'detected_nutrients': list(set([n for m in matches[:5] for n in m['food_data']['key_nutrients']])),
                    'health_score': quality_score,
                    'dietary_balance': quality_rating
                },
                'calorie_analysis': {
                    'total_calories': total_calories,
                    'total_protein': total_protein,
                    'total_carbs': total_carbs,
                    'total_fat': total_fat,
                    'total_fiber': total_fiber,
                    'total_weight_g': total_weight,
                    'calories_per_100g': (total_calories / total_weight * 100) if total_weight > 0 else 0,
                    'detailed_breakdown': detailed_breakdown,
                    'meal_type': matches[0]['food_data']['category'] if matches else 'unknown',
                    'nutritional_quality': {
                        'quality_score': quality_score,
                        'quality_rating': quality_rating,
                        'protein_percentage': protein_pct,
                        'fat_percentage': fat_pct,
                        'fiber_content': total_fiber,
                        'recommendations': [
                            f"Good source of {', '.join(matches[0]['food_data']['key_nutrients'][:2])}" if matches else "",
                            f"Contains {total_fiber}g of fiber per serving" if total_fiber > 2 else "Consider adding more fiber"
                        ]
                    },
                    'dietary_recommendations': [
                        f"This {matches[0]['food_data']['display_name'].lower()} provides {total_calories} calories",
                        f"Rich in {matches[0]['food_data']['key_nutrients'][0]}" if matches and matches[0]['food_data']['key_nutrients'] else ""
                    ]
                },
                'meal_suggestions': [
                    f"Pair with protein for a balanced meal" if matches and matches[0]['food_data']['category'] == 'fruits' else "",
                    f"Great as a snack or breakfast item" if matches and matches[0]['food_data']['category'] == 'fruits' else ""
                ],
                'dietary_labels': [
                    'low-fat' if total_fat < 3 else '',
                    'high-fiber' if total_fiber > 3 else '',
                    'high-protein' if total_protein > 10 else ''
                ]
            }
            
        except Exception as e:
            logger.error(f"Classification error: {e}")
            return {
                'success': False,
                'error': str(e),
                'ingredients': [],
                'confidence': 0.0
            }
    
    def extract_ingredients_from_meal(self, image_bytes: bytes) -> Dict[str, Any]:
        """Extract ingredients (same as classify_food for this implementation)."""
        return self.classify_food(image_bytes)


# Create global instance
food_classifier = LightweightFoodClassifier()

if __name__ == "__main__":
    logger.info("Lightweight Food Classifier is ready!")
    logger.info(f"Supported foods: {', '.join(food_classifier.food_database.keys())}")
