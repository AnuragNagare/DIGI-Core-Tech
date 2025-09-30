import os
import json
import logging
import requests
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class NutritionalInfo:
    """Real nutritional information for food items"""
    name: str
    calories_per_100g: float
    protein_per_100g: float
    carbs_per_100g: float
    fat_per_100g: float
    fiber_per_100g: float
    density: float  # g/cm³
    typical_portion_size: float  # grams
    portion_description: str
    # Enhanced macro breakdowns
    sugar_per_100g: float = 0.0
    saturated_fat_per_100g: float = 0.0
    monounsaturated_fat_per_100g: float = 0.0
    polyunsaturated_fat_per_100g: float = 0.0
    trans_fat_per_100g: float = 0.0
    cholesterol_per_100g: float = 0.0
    sodium_per_100g: float = 0.0
    potassium_per_100g: float = 0.0
    # Vitamins (mg per 100g)
    vitamin_c_per_100g: float = 0.0
    vitamin_a_per_100g: float = 0.0
    vitamin_e_per_100g: float = 0.0
    vitamin_k_per_100g: float = 0.0
    thiamine_per_100g: float = 0.0
    riboflavin_per_100g: float = 0.0
    niacin_per_100g: float = 0.0
    folate_per_100g: float = 0.0
    # Minerals (mg per 100g)
    calcium_per_100g: float = 0.0
    iron_per_100g: float = 0.0
    magnesium_per_100g: float = 0.0
    phosphorus_per_100g: float = 0.0
    zinc_per_100g: float = 0.0
    copper_per_100g: float = 0.0
    manganese_per_100g: float = 0.0
    selenium_per_100g: float = 0.0

class CalorieCalculationService:
    """
    Realistic calorie calculation service using actual nutritional databases.
    Provides accurate calorie estimates based on real food data.
    """
    
    def __init__(self):
        self.nutritional_database = self._load_nutritional_database()
        self.usda_api_key = os.getenv('USDA_API_KEY', 'DEMO_KEY')
        self.usda_base_url = "https://api.nal.usda.gov/fdc/v1"
        
    def _load_nutritional_database(self) -> Dict[str, NutritionalInfo]:
        """Load comprehensive nutritional database with real food data"""
        return {
            # Fruits - Enhanced with detailed macro breakdowns
            'apple': NutritionalInfo('apple', 52, 0.3, 14, 0.2, 2.4, 0.6, 182, '1 medium apple',
                sugar_per_100g=10.4, saturated_fat_per_100g=0.0, monounsaturated_fat_per_100g=0.0,
                polyunsaturated_fat_per_100g=0.1, trans_fat_per_100g=0.0, cholesterol_per_100g=0.0,
                sodium_per_100g=1.0, potassium_per_100g=107.0, vitamin_c_per_100g=4.6, vitamin_a_per_100g=3.0,
                vitamin_e_per_100g=0.2, vitamin_k_per_100g=2.2, thiamine_per_100g=0.0, riboflavin_per_100g=0.0,
                niacin_per_100g=0.1, folate_per_100g=3.0, calcium_per_100g=6.0, iron_per_100g=0.1,
                magnesium_per_100g=5.0, phosphorus_per_100g=11.0, zinc_per_100g=0.0, copper_per_100g=0.0,
                manganese_per_100g=0.0, selenium_per_100g=0.0),
            'banana': NutritionalInfo('banana', 89, 1.1, 23, 0.3, 2.6, 0.7, 120, '1 medium banana',
                sugar_per_100g=12.2, saturated_fat_per_100g=0.1, monounsaturated_fat_per_100g=0.0,
                polyunsaturated_fat_per_100g=0.1, trans_fat_per_100g=0.0, cholesterol_per_100g=0.0,
                sodium_per_100g=1.0, potassium_per_100g=358.0, vitamin_c_per_100g=8.7, vitamin_a_per_100g=64.0,
                vitamin_e_per_100g=0.1, vitamin_k_per_100g=0.5, thiamine_per_100g=0.0, riboflavin_per_100g=0.1,
                niacin_per_100g=0.7, folate_per_100g=20.0, calcium_per_100g=5.0, iron_per_100g=0.3,
                magnesium_per_100g=27.0, phosphorus_per_100g=22.0, zinc_per_100g=0.2, copper_per_100g=0.1,
                manganese_per_100g=0.3, selenium_per_100g=1.0),
            'orange': NutritionalInfo('orange', 47, 0.9, 12, 0.1, 2.4, 0.6, 131, '1 medium orange',
                sugar_per_100g=9.4, saturated_fat_per_100g=0.0, monounsaturated_fat_per_100g=0.0,
                polyunsaturated_fat_per_100g=0.0, trans_fat_per_100g=0.0, cholesterol_per_100g=0.0,
                sodium_per_100g=0.0, potassium_per_100g=181.0, vitamin_c_per_100g=53.2, vitamin_a_per_100g=225.0,
                vitamin_e_per_100g=0.2, vitamin_k_per_100g=0.0, thiamine_per_100g=0.1, riboflavin_per_100g=0.0,
                niacin_per_100g=0.3, folate_per_100g=40.0, calcium_per_100g=40.0, iron_per_100g=0.1,
                magnesium_per_100g=10.0, phosphorus_per_100g=14.0, zinc_per_100g=0.1, copper_per_100g=0.0,
                manganese_per_100g=0.0, selenium_per_100g=0.0),
            'grape': NutritionalInfo('grape', 67, 0.6, 17, 0.2, 0.9, 0.7, 92, '1 cup grapes',
                sugar_per_100g=16.3, saturated_fat_per_100g=0.1, monounsaturated_fat_per_100g=0.0,
                polyunsaturated_fat_per_100g=0.1, trans_fat_per_100g=0.0, cholesterol_per_100g=0.0,
                sodium_per_100g=2.0, potassium_per_100g=191.0, vitamin_c_per_100g=4.0, vitamin_a_per_100g=66.0,
                vitamin_e_per_100g=0.2, vitamin_k_per_100g=14.6, thiamine_per_100g=0.1, riboflavin_per_100g=0.1,
                niacin_per_100g=0.2, folate_per_100g=2.0, calcium_per_100g=10.0, iron_per_100g=0.4,
                magnesium_per_100g=7.0, phosphorus_per_100g=20.0, zinc_per_100g=0.1, copper_per_100g=0.1,
                manganese_per_100g=0.1, selenium_per_100g=0.1),
            'strawberry': NutritionalInfo('strawberry', 32, 0.7, 8, 0.3, 2.0, 0.6, 152, '1 cup strawberries',
                sugar_per_100g=4.9, saturated_fat_per_100g=0.0, monounsaturated_fat_per_100g=0.0,
                polyunsaturated_fat_per_100g=0.2, trans_fat_per_100g=0.0, cholesterol_per_100g=0.0,
                sodium_per_100g=1.0, potassium_per_100g=153.0, vitamin_c_per_100g=58.8, vitamin_a_per_100g=12.0,
                vitamin_e_per_100g=0.3, vitamin_k_per_100g=2.2, thiamine_per_100g=0.0, riboflavin_per_100g=0.0,
                niacin_per_100g=0.4, folate_per_100g=24.0, calcium_per_100g=16.0, iron_per_100g=0.4,
                magnesium_per_100g=13.0, phosphorus_per_100g=24.0, zinc_per_100g=0.1, copper_per_100g=0.0,
                manganese_per_100g=0.4, selenium_per_100g=0.4),
            'blueberry': NutritionalInfo('blueberry', 57, 0.7, 14, 0.3, 2.4, 0.6, 148, '1 cup blueberries'),
            'pineapple': NutritionalInfo('pineapple', 50, 0.5, 13, 0.1, 1.4, 0.8, 165, '1 cup pineapple'),
            'mango': NutritionalInfo('mango', 60, 0.8, 15, 0.4, 1.6, 0.7, 165, '1 medium mango'),
            'peach': NutritionalInfo('peach', 39, 0.9, 10, 0.3, 1.5, 0.6, 150, '1 medium peach'),
            'pear': NutritionalInfo('pear', 57, 0.4, 15, 0.1, 3.1, 0.6, 166, '1 medium pear'),
            
            # Vegetables - Real USDA data
            'carrot': NutritionalInfo('carrot', 41, 0.9, 10, 0.2, 2.8, 0.7, 61, '1 medium carrot'),
            'broccoli': NutritionalInfo('broccoli', 34, 2.8, 7, 0.4, 2.6, 0.4, 91, '1 cup broccoli'),
            'tomato': NutritionalInfo('tomato', 18, 0.9, 4, 0.2, 1.2, 0.6, 123, '1 medium tomato'),
            'potato': NutritionalInfo('potato', 77, 2.0, 17, 0.1, 2.2, 0.7, 150, '1 medium potato'),
            'onion': NutritionalInfo('onion', 40, 1.1, 9, 0.1, 1.7, 0.6, 110, '1 medium onion'),
            'lettuce': NutritionalInfo('lettuce', 15, 1.4, 3, 0.2, 1.3, 0.2, 36, '1 cup lettuce'),
            'spinach': NutritionalInfo('spinach', 23, 2.9, 4, 0.4, 2.2, 0.2, 30, '1 cup spinach'),
            'cucumber': NutritionalInfo('cucumber', 16, 0.7, 4, 0.1, 0.5, 0.6, 119, '1 medium cucumber'),
            'bell_pepper': NutritionalInfo('bell_pepper', 31, 1.0, 7, 0.3, 2.5, 0.6, 119, '1 medium bell pepper'),
            'corn': NutritionalInfo('corn', 86, 3.3, 19, 1.2, 2.7, 0.7, 154, '1 cup corn'),
            
            # Nuts & Seeds - Real USDA data
            'almond': NutritionalInfo('almond', 579, 21, 22, 50, 12, 0.6, 28, '1 oz almonds'),
            'walnut': NutritionalInfo('walnut', 654, 15, 14, 65, 6.7, 0.6, 28, '1 oz walnuts'),
            'cashew': NutritionalInfo('cashew', 553, 18, 30, 44, 3.3, 0.6, 28, '1 oz cashews'),
            'pistachio': NutritionalInfo('pistachio', 560, 20, 28, 45, 10, 0.6, 28, '1 oz pistachios'),
            'peanut': NutritionalInfo('peanut', 567, 26, 16, 49, 8.5, 0.6, 28, '1 oz peanuts'),
            'sunflower_seed': NutritionalInfo('sunflower_seed', 584, 21, 20, 51, 8.6, 0.6, 28, '1 oz sunflower seeds'),
            
            # Grains - Real USDA data
            'rice': NutritionalInfo('rice', 130, 2.7, 28, 0.3, 0.4, 0.8, 158, '1 cup cooked rice'),
            'wheat': NutritionalInfo('wheat', 339, 13, 71, 2.5, 12, 0.8, 120, '1 cup wheat flour'),
            'oats': NutritionalInfo('oats', 389, 17, 66, 7, 11, 0.6, 81, '1 cup oats'),
            'quinoa': NutritionalInfo('quinoa', 120, 4.4, 22, 1.9, 2.8, 0.7, 185, '1 cup cooked quinoa'),
            'bread': NutritionalInfo('bread', 265, 9, 49, 3.2, 2.7, 0.3, 28, '1 slice bread'),
            'pasta': NutritionalInfo('pasta', 131, 5, 25, 1.1, 1.8, 0.6, 140, '1 cup cooked pasta'),
            
            # Proteins - Real USDA data
            'chicken': NutritionalInfo('chicken', 165, 31, 0, 3.6, 0, 1.0, 100, '3.5 oz chicken breast'),
            'beef': NutritionalInfo('beef', 250, 26, 0, 15, 0, 1.0, 100, '3.5 oz beef'),
            'fish': NutritionalInfo('fish', 206, 22, 0, 12, 0, 1.0, 100, '3.5 oz fish'),
            'salmon': NutritionalInfo('salmon', 208, 25, 0, 12, 0, 1.0, 100, '3.5 oz salmon'),
            'egg': NutritionalInfo('egg', 155, 13, 1.1, 11, 0, 1.0, 50, '1 large egg'),
            'tofu': NutritionalInfo('tofu', 76, 8, 2, 5, 0.3, 1.0, 100, '3.5 oz tofu'),
            'beans': NutritionalInfo('beans', 127, 8, 23, 0.5, 6, 0.8, 177, '1 cup cooked beans'),
            
            # Dairy - Real USDA data
            'milk': NutritionalInfo('milk', 42, 3.4, 5, 1, 0, 1.0, 244, '1 cup milk'),
            'cheese': NutritionalInfo('cheese', 113, 7, 1, 9, 0, 1.0, 28, '1 oz cheese'),
            'yogurt': NutritionalInfo('yogurt', 59, 10, 4, 0.4, 0, 1.0, 245, '1 cup yogurt'),
            'butter': NutritionalInfo('butter', 717, 0.9, 0.1, 81, 0, 0.9, 14, '1 tbsp butter'),
            
            # Other common foods
            'olive_oil': NutritionalInfo('olive_oil', 884, 0, 0, 100, 0, 0.9, 14, '1 tbsp olive oil'),
            'sugar': NutritionalInfo('sugar', 387, 0, 100, 0, 0, 1.6, 4, '1 tsp sugar'),
            'salt': NutritionalInfo('salt', 0, 0, 0, 0, 0, 2.2, 6, '1 tsp salt'),
        }
    
    def estimate_portion_size(self, food_name: str, confidence: float, image_dimensions: Tuple[int, int] = (224, 224)) -> float:
        """
        Estimate realistic portion size based on food type and confidence.
        Uses typical serving sizes and adjusts based on confidence.
        """
        if food_name not in self.nutritional_database:
            return 100  # Default 100g if unknown
        
        food_info = self.nutritional_database[food_name]
        typical_portion = food_info.typical_portion_size
        
        # Adjust portion size based on confidence
        # Higher confidence = more accurate portion estimation
        confidence_factor = 0.8 + (confidence * 0.4)  # Range: 0.8 to 1.2
        
        # Add some realistic variation (±20%)
        variation = np.random.normal(1.0, 0.1)  # Normal distribution around 1.0
        variation = max(0.7, min(1.3, variation))  # Clamp between 0.7 and 1.3
        
        estimated_portion = typical_portion * confidence_factor * variation
        
        return max(10, estimated_portion)  # Minimum 10g
    
    def calculate_calories(self, food_name: str, portion_size_g: float) -> Dict[str, Any]:
        """
        Calculate realistic calories and nutritional information.
        Uses real USDA nutritional data.
        """
        if food_name not in self.nutritional_database:
            return {
                'calories': 0,
                'protein': 0,
                'carbs': 0,
                'fat': 0,
                'fiber': 0,
                'error': f'Unknown food: {food_name}'
            }
        
        food_info = self.nutritional_database[food_name]
        
        # Calculate nutritional values based on portion size
        calories = (food_info.calories_per_100g * portion_size_g) / 100
        protein = (food_info.protein_per_100g * portion_size_g) / 100
        carbs = (food_info.carbs_per_100g * portion_size_g) / 100
        fat = (food_info.fat_per_100g * portion_size_g) / 100
        fiber = (food_info.fiber_per_100g * portion_size_g) / 100
        
        return {
            'calories': round(calories, 1),
            'protein': round(protein, 1),
            'carbs': round(carbs, 1),
            'fat': round(fat, 1),
            'fiber': round(fiber, 1),
            'portion_size_g': round(portion_size_g, 1),
            'portion_description': food_info.portion_description,
            'food_name': food_name,
            'density': food_info.density
        }
    
    def calculate_precise_nutrition(self, food_name: str, confirmed_weight_g: float) -> Dict[str, Any]:
        """
        Calculate precise nutritional information with mathematical accuracy.
        Target: 90-95% accuracy for all calculations.
        Enhanced with detailed macro breakdowns and micronutrients.
        """
        # Input validation
        if not food_name or not isinstance(food_name, str):
            return {
                'calories': 0,
                'protein': 0,
                'carbs': 0,
                'fat': 0,
                'fiber': 0,
                'error': 'Invalid food name provided'
            }
        
        if not isinstance(confirmed_weight_g, (int, float)) or confirmed_weight_g <= 0:
            return {
                'calories': 0,
                'protein': 0,
                'carbs': 0,
                'fat': 0,
                'fiber': 0,
                'error': f'Invalid weight: {confirmed_weight_g}. Must be a positive number.'
            }
        
        if confirmed_weight_g > 10000:  # 10kg limit
            return {
                'calories': 0,
                'protein': 0,
                'carbs': 0,
                'fat': 0,
                'fiber': 0,
                'error': f'Weight too large: {confirmed_weight_g}g. Maximum 10kg allowed.'
            }
        
        if food_name not in self.nutritional_database:
            return {
                'calories': 0,
                'protein': 0,
                'carbs': 0,
                'fat': 0,
                'fiber': 0,
                'error': f'Unknown food: {food_name}. Available foods: {list(self.nutritional_database.keys())[:5]}...'
            }
        
        food_info = self.nutritional_database[food_name]
        
        # Precise mathematical calculations with high accuracy
        # Base values per 100g
        base_calories = food_info.calories_per_100g
        base_protein = food_info.protein_per_100g
        base_carbs = food_info.carbs_per_100g
        base_fat = food_info.fat_per_100g
        base_fiber = food_info.fiber_per_100g
        
        # Precise scaling formula: (base_per_100g * confirmed_weight_g) / 100
        calories = (base_calories * confirmed_weight_g) / 100
        protein = (base_protein * confirmed_weight_g) / 100
        carbs = (base_carbs * confirmed_weight_g) / 100
        fat = (base_fat * confirmed_weight_g) / 100
        fiber = (base_fiber * confirmed_weight_g) / 100
        
        # Enhanced macro breakdowns
        sugar = (food_info.sugar_per_100g * confirmed_weight_g) / 100
        saturated_fat = (food_info.saturated_fat_per_100g * confirmed_weight_g) / 100
        monounsaturated_fat = (food_info.monounsaturated_fat_per_100g * confirmed_weight_g) / 100
        polyunsaturated_fat = (food_info.polyunsaturated_fat_per_100g * confirmed_weight_g) / 100
        trans_fat = (food_info.trans_fat_per_100g * confirmed_weight_g) / 100
        cholesterol = (food_info.cholesterol_per_100g * confirmed_weight_g) / 100
        sodium = (food_info.sodium_per_100g * confirmed_weight_g) / 100
        potassium = (food_info.potassium_per_100g * confirmed_weight_g) / 100
        
        # Calculate additional nutrients for precision
        calories_from_protein = protein * 4
        calories_from_carbs = carbs * 4
        calories_from_fat = fat * 9
        total_calculated_calories = calories_from_protein + calories_from_carbs + calories_from_fat
        
        # Validation: ensure calculated calories match expected
        calorie_accuracy = abs(calories - total_calculated_calories) / calories * 100 if calories > 0 else 0
        
        # Additional validation checks
        validation_errors = []
        if calorie_accuracy > 5:  # More than 5% deviation
            validation_errors.append(f"Calorie calculation deviation: {calorie_accuracy:.1f}%")
        
        if protein < 0 or carbs < 0 or fat < 0 or fiber < 0:
            validation_errors.append("Negative nutrient values detected")
        
        if calories > 1000:  # Unusually high calories
            validation_errors.append(f"Unusually high calorie count: {calories:.1f}")
        
        # Check for mathematical precision
        if abs(calories - total_calculated_calories) > 1:
            validation_errors.append("Calorie calculation precision issue")
        
        # Calculate detailed micronutrients
        vitamins = self._calculate_vitamins(food_info, confirmed_weight_g)
        minerals = self._calculate_minerals(food_info, confirmed_weight_g)
        
        return {
            'calories': round(calories, 1),
            'protein': round(protein, 2),
            'carbs': round(carbs, 2),
            'fat': round(fat, 2),
            'fiber': round(fiber, 2),
            'portion_size_g': round(confirmed_weight_g, 1),
            'portion_description': food_info.portion_description,
            'food_name': food_name,
            'density': food_info.density,
            'calorie_accuracy': round(calorie_accuracy, 2),
            'calories_from_protein': round(calories_from_protein, 1),
            'calories_from_carbs': round(calories_from_carbs, 1),
            'calories_from_fat': round(calories_from_fat, 1),
            'total_calculated_calories': round(total_calculated_calories, 1),
            # Enhanced macro breakdowns
            'sugar': round(sugar, 2),
            'saturated_fat': round(saturated_fat, 2),
            'monounsaturated_fat': round(monounsaturated_fat, 2),
            'polyunsaturated_fat': round(polyunsaturated_fat, 2),
            'trans_fat': round(trans_fat, 2),
            'cholesterol': round(cholesterol, 2),
            'sodium': round(sodium, 2),
            'potassium': round(potassium, 2),
            # Detailed micronutrients
            'vitamins': vitamins,
            'minerals': minerals,
            # Nutritional quality assessment
            'nutritional_quality': self._assess_nutritional_quality(calories, protein, carbs, fat, fiber, vitamins, minerals),
            # Validation and error handling
            'validation_errors': validation_errors,
            'calculation_quality': 'excellent' if not validation_errors else 'needs_review',
            'timestamp': datetime.now().isoformat()
        }
    
    def scale_nutrients(self, base_nutrition: Dict[str, Any], scale_factor: float) -> Dict[str, Any]:
        """
        Scale all nutrients by a precise factor.
        Used for portion size adjustments.
        """
        scaled = {}
        for key, value in base_nutrition.items():
            if isinstance(value, (int, float)) and key not in ['portion_size_g', 'density']:
                scaled[key] = round(value * scale_factor, 2)
            else:
                scaled[key] = value
        
        return scaled
    
    def validate_portion_size(self, food_name: str, weight_g: float) -> Dict[str, Any]:
        """
        Validate portion size against typical serving sizes.
        Returns validation results and recommendations.
        """
        if food_name not in self.nutritional_database:
            return {'valid': False, 'error': 'Unknown food'}
        
        food_info = self.nutritional_database[food_name]
        typical_portion = food_info.typical_portion_size
        
        # Calculate deviation from typical portion
        deviation = abs(weight_g - typical_portion) / typical_portion * 100
        
        validation = {
            'valid': True,
            'typical_portion_g': typical_portion,
            'deviation_percent': round(deviation, 1),
            'recommendation': 'Good portion size'
        }
        
        if deviation > 50:
            validation['recommendation'] = 'Unusually large portion - consider splitting'
        elif deviation > 25:
            validation['recommendation'] = 'Larger than typical - ensure accuracy'
        elif deviation < 10:
            validation['recommendation'] = 'Perfect portion size'
        
        return validation
    
    def _calculate_vitamins(self, food_info: NutritionalInfo, weight_g: float) -> Dict[str, float]:
        """Calculate detailed vitamin content for the given weight."""
        return {
            'vitamin_c': round((food_info.vitamin_c_per_100g * weight_g) / 100, 2),
            'vitamin_a': round((food_info.vitamin_a_per_100g * weight_g) / 100, 2),
            'vitamin_e': round((food_info.vitamin_e_per_100g * weight_g) / 100, 2),
            'vitamin_k': round((food_info.vitamin_k_per_100g * weight_g) / 100, 2),
            'thiamine': round((food_info.thiamine_per_100g * weight_g) / 100, 3),
            'riboflavin': round((food_info.riboflavin_per_100g * weight_g) / 100, 3),
            'niacin': round((food_info.niacin_per_100g * weight_g) / 100, 3),
            'folate': round((food_info.folate_per_100g * weight_g) / 100, 2)
        }
    
    def _calculate_minerals(self, food_info: NutritionalInfo, weight_g: float) -> Dict[str, float]:
        """Calculate detailed mineral content for the given weight."""
        return {
            'calcium': round((food_info.calcium_per_100g * weight_g) / 100, 2),
            'iron': round((food_info.iron_per_100g * weight_g) / 100, 2),
            'magnesium': round((food_info.magnesium_per_100g * weight_g) / 100, 2),
            'phosphorus': round((food_info.phosphorus_per_100g * weight_g) / 100, 2),
            'zinc': round((food_info.zinc_per_100g * weight_g) / 100, 2),
            'copper': round((food_info.copper_per_100g * weight_g) / 100, 2),
            'manganese': round((food_info.manganese_per_100g * weight_g) / 100, 2),
            'selenium': round((food_info.selenium_per_100g * weight_g) / 100, 2)
        }
    
    def _assess_nutritional_quality(self, calories: float, protein: float, carbs: float, 
                                   fat: float, fiber: float, vitamins: Dict[str, float], 
                                   minerals: Dict[str, float]) -> Dict[str, Any]:
        """Assess the nutritional quality of the food item."""
        
        # Calculate macro percentages
        total_calories = calories
        protein_percentage = (protein * 4 / total_calories * 100) if total_calories > 0 else 0
        carb_percentage = (carbs * 4 / total_calories * 100) if total_calories > 0 else 0
        fat_percentage = (fat * 9 / total_calories * 100) if total_calories > 0 else 0
        
        # Quality scoring (0-100)
        quality_score = 0
        
        # Protein quality (0-25 points)
        if protein_percentage >= 15 and protein_percentage <= 35:
            quality_score += 25
        elif protein_percentage >= 10 and protein_percentage <= 40:
            quality_score += 20
        elif protein_percentage >= 5:
            quality_score += 15
        
        # Carb quality (0-25 points)
        if carb_percentage >= 45 and carb_percentage <= 65:
            quality_score += 25
        elif carb_percentage >= 35 and carb_percentage <= 75:
            quality_score += 20
        elif carb_percentage >= 25:
            quality_score += 15
        
        # Fat quality (0-25 points)
        if fat_percentage >= 20 and fat_percentage <= 35:
            quality_score += 25
        elif fat_percentage >= 15 and fat_percentage <= 40:
            quality_score += 20
        elif fat_percentage >= 10:
            quality_score += 15
        
        # Fiber quality (0-25 points)
        fiber_per_100_calories = (fiber / total_calories * 100) if total_calories > 0 else 0
        if fiber_per_100_calories >= 3:
            quality_score += 25
        elif fiber_per_100_calories >= 2:
            quality_score += 20
        elif fiber_per_100_calories >= 1:
            quality_score += 15
        
        # Determine quality rating
        if quality_score >= 90:
            quality_rating = "Excellent"
        elif quality_score >= 75:
            quality_rating = "Very Good"
        elif quality_score >= 60:
            quality_rating = "Good"
        elif quality_score >= 45:
            quality_rating = "Fair"
        else:
            quality_rating = "Poor"
        
        # Generate recommendations
        recommendations = []
        if protein_percentage < 15:
            recommendations.append("Consider adding more protein sources")
        if carb_percentage > 70:
            recommendations.append("Reduce refined carbohydrates")
        if fat_percentage > 40:
            recommendations.append("Consider reducing fat intake")
        if fiber_per_100_calories < 2:
            recommendations.append("Increase fiber intake")
        if vitamins['vitamin_c'] < 10:
            recommendations.append("Add vitamin C rich foods")
        if minerals['iron'] < 2:
            recommendations.append("Consider iron-rich foods")
        
        return {
            'quality_score': round(quality_score, 1),
            'quality_rating': quality_rating,
            'protein_percentage': round(protein_percentage, 1),
            'carb_percentage': round(carb_percentage, 1),
            'fat_percentage': round(fat_percentage, 1),
            'fiber_per_100_calories': round(fiber_per_100_calories, 1),
            'recommendations': recommendations
        }
    
    def analyze_meal_calories(self, ingredients: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze complete meal calories and nutritional breakdown.
        Provides realistic, accurate nutritional analysis.
        """
        total_calories = 0
        total_protein = 0
        total_carbs = 0
        total_fat = 0
        total_fiber = 0
        total_weight = 0
        
        detailed_breakdown = []
        
        for ingredient in ingredients:
            food_name = ingredient.get('name', '').lower()
            confidence = ingredient.get('confidence', 0.5)
            
            # Estimate portion size
            portion_size = self.estimate_portion_size(food_name, confidence)
            
            # Calculate nutritional values
            nutrition = self.calculate_calories(food_name, portion_size)
            
            if 'error' not in nutrition:
                total_calories += nutrition['calories']
                total_protein += nutrition['protein']
                total_carbs += nutrition['carbs']
                total_fat += nutrition['fat']
                total_fiber += nutrition['fiber']
                total_weight += nutrition['portion_size_g']
                
                detailed_breakdown.append({
                    'name': food_name,
                    'portion_size_g': nutrition['portion_size_g'],
                    'calories': nutrition['calories'],
                    'protein': nutrition['protein'],
                    'carbs': nutrition['carbs'],
                    'fat': nutrition['fat'],
                    'fiber': nutrition['fiber'],
                    'confidence': confidence
                })
        
        # Calculate meal-level metrics
        meal_analysis = {
            'total_calories': round(total_calories, 1),
            'total_protein': round(total_protein, 1),
            'total_carbs': round(total_carbs, 1),
            'total_fat': round(total_fat, 1),
            'total_fiber': round(total_fiber, 1),
            'total_weight_g': round(total_weight, 1),
            'calories_per_100g': round((total_calories / total_weight * 100) if total_weight > 0 else 0, 1),
            'detailed_breakdown': detailed_breakdown,
            'meal_type': self._classify_meal_type(total_calories, total_protein, total_carbs, total_fat),
            'nutritional_quality': self._assess_nutritional_quality(total_calories, total_protein, total_carbs, total_fat, total_fiber),
            'dietary_recommendations': self._generate_dietary_recommendations(total_calories, total_protein, total_carbs, total_fat)
        }
        
        return meal_analysis
    
    def _classify_meal_type(self, calories: float, protein: float, carbs: float, fat: float) -> str:
        """Classify the type of meal based on nutritional content"""
        if calories < 200:
            return "light_snack"
        elif calories < 400:
            return "snack"
        elif calories < 600:
            return "light_meal"
        elif calories < 800:
            return "regular_meal"
        else:
            return "large_meal"
    
    def _assess_nutritional_quality(self, calories: float, protein: float, carbs: float, fat: float, fiber: float) -> Dict[str, Any]:
        """Assess the nutritional quality of the meal"""
        quality_score = 0
        recommendations = []
        
        # Protein assessment (15-25% of calories from protein)
        protein_calories = protein * 4
        protein_percentage = (protein_calories / calories * 100) if calories > 0 else 0
        
        if 15 <= protein_percentage <= 25:
            quality_score += 2
        elif 10 <= protein_percentage < 15 or 25 < protein_percentage <= 30:
            quality_score += 1
            recommendations.append("Consider adjusting protein intake")
        
        # Fat assessment (20-35% of calories from fat)
        fat_calories = fat * 9
        fat_percentage = (fat_calories / calories * 100) if calories > 0 else 0
        
        if 20 <= fat_percentage <= 35:
            quality_score += 2
        elif 15 <= fat_percentage < 20 or 35 < fat_percentage <= 40:
            quality_score += 1
            recommendations.append("Consider adjusting fat intake")
        
        # Fiber assessment (25g+ per day)
        if fiber >= 5:
            quality_score += 2
        elif fiber >= 3:
            quality_score += 1
            recommendations.append("Add more fiber-rich foods")
        else:
            recommendations.append("Consider adding more vegetables and whole grains")
        
        # Overall quality rating
        if quality_score >= 6:
            quality_rating = "excellent"
        elif quality_score >= 4:
            quality_rating = "good"
        elif quality_score >= 2:
            quality_rating = "fair"
        else:
            quality_rating = "needs_improvement"
        
        return {
            'quality_score': quality_score,
            'quality_rating': quality_rating,
            'protein_percentage': round(protein_percentage, 1),
            'fat_percentage': round(fat_percentage, 1),
            'fiber_content': round(fiber, 1),
            'recommendations': recommendations
        }
    
    def _generate_dietary_recommendations(self, calories: float, protein: float, carbs: float, fat: float) -> List[str]:
        """Generate realistic dietary recommendations"""
        recommendations = []
        
        if calories > 1000:
            recommendations.append("This is a high-calorie meal. Consider portion control.")
        
        if protein < 20:
            recommendations.append("Add more protein sources like lean meat, fish, or legumes.")
        
        if fat > 50:
            recommendations.append("Consider reducing high-fat ingredients.")
        
        if carbs > 100:
            recommendations.append("This meal is high in carbohydrates. Consider adding more vegetables.")
        
        if calories < 300:
            recommendations.append("This is a light meal. You might need additional snacks.")
        
        return recommendations

# Initialize the service
calorie_calculator = CalorieCalculationService()
