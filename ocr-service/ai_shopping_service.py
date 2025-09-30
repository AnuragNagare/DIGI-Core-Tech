#!/usr/bin/env python3
"""
AI Shopping List Service
Advanced machine learning system for intelligent shopping list generation
"""

import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict, Counter
import pickle
import os

@dataclass
class ShoppingItem:
    name: str
    category: str
    brand: Optional[str] = None
    price: Optional[float] = None
    quantity: int = 1
    unit: str = "piece"
    priority_score: float = 0.0
    confidence: float = 0.0
    reason: str = ""

@dataclass
class UserPattern:
    user_id: str
    item_frequencies: Dict[str, int]
    category_preferences: Dict[str, float]
    seasonal_patterns: Dict[str, Dict[str, float]]
    time_patterns: Dict[str, List[int]]  # day_of_week patterns
    budget_patterns: Dict[str, float]

class PatternAnalyzer:
    """Analyzes user shopping patterns and preferences"""
    
    def __init__(self):
        self.user_patterns = {}
        self.global_patterns = {}
        
    def analyze_shopping_history(self, user_id: str, shopping_history: List[Dict]) -> UserPattern:
        """Analyze user's shopping history to extract patterns"""
        item_frequencies = Counter()
        category_counts = Counter()
        seasonal_patterns = defaultdict(lambda: defaultdict(float))
        time_patterns = defaultdict(list)
        budget_patterns = {}
        
        for entry in shopping_history:
            date = datetime.fromisoformat(entry.get('date', datetime.now().isoformat()))
            items = entry.get('items', [])
            total_cost = entry.get('total_cost', 0)
            
            # Analyze item frequencies
            for item in items:
                item_name = item.get('name', '')
                category = item.get('category', 'other')
                item_frequencies[item_name] += 1
                category_counts[category] += 1
                
                # Seasonal patterns (month-based)
                month = date.strftime('%B')
                seasonal_patterns[month][category] += 1
                
                # Time patterns (day of week)
                time_patterns[item_name].append(date.weekday())
            
            # Budget patterns (monthly spending)
            month_year = date.strftime('%Y-%m')
            if month_year not in budget_patterns:
                budget_patterns[month_year] = []
            budget_patterns[month_year].append(total_cost)
        
        # Calculate category preferences (normalized)
        total_items = sum(category_counts.values())
        category_preferences = {
            cat: count / total_items for cat, count in category_counts.items()
        }
        
        # Average budget patterns
        avg_budget_patterns = {
            month: np.mean(costs) for month, costs in budget_patterns.items()
        }
        
        pattern = UserPattern(
            user_id=user_id,
            item_frequencies=dict(item_frequencies),
            category_preferences=category_preferences,
            seasonal_patterns=dict(seasonal_patterns),
            time_patterns=dict(time_patterns),
            budget_patterns=avg_budget_patterns
        )
        
        self.user_patterns[user_id] = pattern
        return pattern

class PredictionEngine:
    """ML-based prediction engine for shopping recommendations"""
    
    def __init__(self):
        self.models = {}
        self.item_similarity_matrix = {}
        self.global_trends = {}
        
    def predict_needed_items(self, user_id: str, current_inventory: List[Dict], 
                           user_pattern: UserPattern) -> List[ShoppingItem]:
        """Predict what items user likely needs"""
        predictions = []
        current_items = {item['name']: item for item in current_inventory}
        
        # 1. Frequency-based predictions
        frequent_items = self._predict_by_frequency(user_pattern, current_items)
        predictions.extend(frequent_items)
        
        # 2. Seasonal predictions  
        seasonal_items = self._predict_seasonal_items(user_pattern, current_items)
        predictions.extend(seasonal_items)
        
        # 3. Category-based predictions
        category_items = self._predict_by_categories(user_pattern, current_items)
        predictions.extend(category_items)
        
        # 4. Replenishment predictions
        replenishment_items = self._predict_replenishments(current_inventory, user_pattern)
        predictions.extend(replenishment_items)
        
        # Remove duplicates and sort by confidence
        unique_predictions = self._deduplicate_predictions(predictions)
        return sorted(unique_predictions, key=lambda x: x.confidence, reverse=True)
    
    def _predict_by_frequency(self, user_pattern: UserPattern, current_items: Dict) -> List[ShoppingItem]:
        """Predict items based on purchase frequency"""
        predictions = []
        
        # Find frequently bought items that are missing
        for item_name, frequency in user_pattern.item_frequencies.items():
            if item_name not in current_items and frequency > 2:  # Bought more than twice
                confidence = min(frequency / 10.0, 0.9)  # Cap confidence at 90%
                predictions.append(ShoppingItem(
                    name=item_name,
                    category=self._get_item_category(item_name, user_pattern),
                    confidence=confidence,
                    reason=f"Frequently purchased ({frequency} times)"
                ))
        
        return predictions
    
    def _predict_seasonal_items(self, user_pattern: UserPattern, current_items: Dict) -> List[ShoppingItem]:
        """Predict items based on seasonal patterns"""
        predictions = []
        current_month = datetime.now().strftime('%B')
        
        if current_month in user_pattern.seasonal_patterns:
            seasonal_cats = user_pattern.seasonal_patterns[current_month]
            
            for category, frequency in seasonal_cats.items():
                if frequency > 1:  # Category bought more than once in this season
                    # Predict common items in this category
                    seasonal_items = self._get_seasonal_category_items(category, current_month)
                    for item in seasonal_items:
                        if item not in current_items:
                            predictions.append(ShoppingItem(
                                name=item,
                                category=category,
                                confidence=0.7,
                                reason=f"Seasonal trend for {current_month}"
                            ))
        
        return predictions
    
    def _predict_by_categories(self, user_pattern: UserPattern, current_items: Dict) -> List[ShoppingItem]:
        """Predict items based on category preferences"""
        predictions = []
        
        # Check which preferred categories are underrepresented in current inventory
        current_categories = Counter(item.get('category', 'other') for item in current_items.values())
        total_current = sum(current_categories.values()) or 1
        
        for category, preference in user_pattern.category_preferences.items():
            current_ratio = current_categories[category] / total_current
            
            # If category is underrepresented compared to user's preference
            if current_ratio < preference * 0.5:  # Less than 50% of expected
                category_items = self._get_common_category_items(category)
                for item in category_items[:2]:  # Top 2 items from category
                    if item not in current_items:
                        predictions.append(ShoppingItem(
                            name=item,
                            category=category,
                            confidence=0.6,
                            reason=f"Category preference: {category}"
                        ))
        
        return predictions
    
    def _predict_replenishments(self, current_inventory: List[Dict], user_pattern: UserPattern) -> List[ShoppingItem]:
        """Predict items that need replenishment"""
        predictions = []
        
        for item in current_inventory:
            item_name = item.get('name', '')
            quantity = float(item.get('quantity', 0))
            days_left = item.get('daysLeft', 999)
            
            # Check if item is running low and user buys it frequently
            if (quantity <= 2 or days_left <= 3) and item_name in user_pattern.item_frequencies:
                frequency = user_pattern.item_frequencies[item_name]
                if frequency > 1:  # User buys this item regularly
                    predictions.append(ShoppingItem(
                        name=item_name,
                        category=item.get('category', 'other'),
                        quantity=int(frequency / 2) + 1,  # Smart quantity prediction
                        confidence=0.85,
                        reason=f"Running low (frequent purchase)"
                    ))
        
        return predictions
    
    def _deduplicate_predictions(self, predictions: List[ShoppingItem]) -> List[ShoppingItem]:
        """Remove duplicate predictions, keeping highest confidence"""
        item_dict = {}
        
        for prediction in predictions:
            if prediction.name not in item_dict:
                item_dict[prediction.name] = prediction
            else:
                # Keep higher confidence prediction
                if prediction.confidence > item_dict[prediction.name].confidence:
                    item_dict[prediction.name] = prediction
        
        return list(item_dict.values())
    
    def _get_item_category(self, item_name: str, user_pattern: UserPattern) -> str:
        """Get category for an item"""
        # Simple category mapping (could be enhanced with ML)
        category_keywords = {
            'fruits': ['apple', 'banana', 'orange', 'grape', 'strawberry'],
            'vegetables': ['tomato', 'onion', 'carrot', 'lettuce', 'potato'],
            'dairy': ['milk', 'cheese', 'yogurt', 'butter', 'cream'],
            'meat': ['chicken', 'beef', 'pork', 'fish', 'turkey'],
            'grains': ['bread', 'rice', 'pasta', 'oats', 'cereal']
        }
        
        item_lower = item_name.lower()
        for category, keywords in category_keywords.items():
            if any(keyword in item_lower for keyword in keywords):
                return category
        
        return 'other'
    
    def _get_seasonal_category_items(self, category: str, month: str) -> List[str]:
        """Get seasonal items for a category"""
        seasonal_items = {
            'fruits': {
                'January': ['apple', 'orange', 'grapefruit'],
                'April': ['strawberry', 'apricot'],
                'July': ['watermelon', 'peach', 'berries'],
                'October': ['pumpkin', 'apple', 'pear']
            },
            'vegetables': {
                'January': ['cabbage', 'carrot', 'onion'],
                'April': ['asparagus', 'lettuce'],
                'July': ['tomato', 'cucumber', 'corn'],
                'October': ['pumpkin', 'squash', 'potato']
            }
        }
        
        return seasonal_items.get(category, {}).get(month, [])
    
    def _get_common_category_items(self, category: str) -> List[str]:
        """Get common items for a category"""
        common_items = {
            'fruits': ['banana', 'apple', 'orange'],
            'vegetables': ['tomato', 'onion', 'potato'],
            'dairy': ['milk', 'cheese', 'yogurt'],
            'meat': ['chicken', 'ground beef'],
            'grains': ['bread', 'rice', 'pasta'],
            'other': ['salt', 'pepper', 'oil']
        }
        
        return common_items.get(category, [])

class PrioritizationService:
    """Intelligent prioritization of shopping items"""
    
    def prioritize_items(self, items: List[ShoppingItem], user_pattern: UserPattern, 
                        budget_limit: Optional[float] = None) -> List[ShoppingItem]:
        """Prioritize shopping items intelligently"""
        
        for item in items:
            priority_score = self._calculate_priority_score(item, user_pattern)
            item.priority_score = priority_score
        
        # Sort by priority score (higher = more important)
        prioritized_items = sorted(items, key=lambda x: x.priority_score, reverse=True)
        
        # Apply budget constraints if specified
        if budget_limit:
            prioritized_items = self._apply_budget_constraints(prioritized_items, budget_limit)
        
        return prioritized_items
    
    def _calculate_priority_score(self, item: ShoppingItem, user_pattern: UserPattern) -> float:
        """Calculate priority score for an item"""
        score = 0.0
        
        # Base confidence score (40% weight)
        score += item.confidence * 0.4
        
        # Frequency factor (30% weight)
        frequency = user_pattern.item_frequencies.get(item.name, 0)
        frequency_score = min(frequency / 5.0, 1.0)  # Normalize to 0-1
        score += frequency_score * 0.3
        
        # Category preference factor (20% weight)
        category_pref = user_pattern.category_preferences.get(item.category, 0.1)
        score += category_pref * 0.2
        
        # Urgency factor (10% weight)
        urgency_keywords = ['running low', 'expiring', 'out of']
        if any(keyword in item.reason.lower() for keyword in urgency_keywords):
            score += 0.1
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _apply_budget_constraints(self, items: List[ShoppingItem], budget_limit: float) -> List[ShoppingItem]:
        """Apply budget constraints to item list"""
        total_cost = 0.0
        budget_aware_items = []
        
        for item in items:
            estimated_cost = item.price or self._estimate_item_cost(item)
            
            if total_cost + estimated_cost <= budget_limit:
                budget_aware_items.append(item)
                total_cost += estimated_cost
            elif total_cost < budget_limit * 0.9:  # Allow 10% buffer
                budget_aware_items.append(item)
                break
        
        return budget_aware_items
    
    def _estimate_item_cost(self, item: ShoppingItem) -> float:
        """Estimate cost of an item"""
        # Simple cost estimation (could be enhanced with real pricing data)
        cost_estimates = {
            'fruits': 3.0,
            'vegetables': 2.5,
            'dairy': 4.0,
            'meat': 8.0,
            'grains': 3.5,
            'other': 2.0
        }
        
        base_cost = cost_estimates.get(item.category, 3.0)
        return base_cost * item.quantity

class AIShoppingService:
    """Main AI Shopping Service"""
    
    def __init__(self):
        self.pattern_analyzer = PatternAnalyzer()
        self.prediction_engine = PredictionEngine()
        self.prioritization_service = PrioritizationService()
        
        # Load any existing models/data
        self._load_models()
    
    def generate_smart_shopping_list(self, user_id: str, current_inventory: List[Dict], 
                                   shopping_history: List[Dict], 
                                   budget_limit: Optional[float] = None) -> Dict:
        """Generate intelligent shopping list"""
        
        try:
            # Analyze user patterns
            user_pattern = self.pattern_analyzer.analyze_shopping_history(user_id, shopping_history)
            
            # Predict needed items
            predicted_items = self.prediction_engine.predict_needed_items(
                user_id, current_inventory, user_pattern
            )
            
            # Prioritize items
            prioritized_items = self.prioritization_service.prioritize_items(
                predicted_items, user_pattern, budget_limit
            )
            
            # Generate insights
            insights = self._generate_insights(user_pattern, prioritized_items)
            
            return {
                'success': True,
                'shopping_list': [self._item_to_dict(item) for item in prioritized_items],
                'total_items': len(prioritized_items),
                'insights': insights,
                'user_patterns': {
                    'top_categories': list(user_pattern.category_preferences.keys())[:3],
                    'shopping_frequency': len(shopping_history),
                    'predicted_budget': sum(item.price or 3.0 for item in prioritized_items)
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'shopping_list': [],
                'insights': {}
            }
    
    def learn_from_feedback(self, user_id: str, item_name: str, feedback: str):
        """Learn from user feedback to improve predictions"""
        # Simple learning mechanism (could be enhanced)
        if user_id in self.pattern_analyzer.user_patterns:
            pattern = self.pattern_analyzer.user_patterns[user_id]
            
            if feedback == 'positive':
                pattern.item_frequencies[item_name] = pattern.item_frequencies.get(item_name, 0) + 1
            elif feedback == 'negative':
                pattern.item_frequencies[item_name] = max(pattern.item_frequencies.get(item_name, 1) - 1, 0)
    
    def get_shopping_insights(self, user_id: str) -> Dict:
        """Get shopping insights and patterns"""
        if user_id not in self.pattern_analyzer.user_patterns:
            return {'insights': 'No shopping history available'}
        
        pattern = self.pattern_analyzer.user_patterns[user_id]
        
        insights = {
            'top_items': list(sorted(pattern.item_frequencies.items(), key=lambda x: x[1], reverse=True)[:5]),
            'favorite_categories': list(sorted(pattern.category_preferences.items(), key=lambda x: x[1], reverse=True)[:3]),
            'seasonal_trends': pattern.seasonal_patterns,
            'shopping_recommendations': self._get_general_recommendations(pattern)
        }
        
        return insights
    
    def _generate_insights(self, user_pattern: UserPattern, items: List[ShoppingItem]) -> Dict:
        """Generate shopping insights"""
        return {
            'prediction_confidence': np.mean([item.confidence for item in items]) if items else 0,
            'categories_predicted': len(set(item.category for item in items)),
            'seasonal_items': len([item for item in items if 'seasonal' in item.reason.lower()]),
            'frequent_items': len([item for item in items if 'frequent' in item.reason.lower()]),
            'smart_suggestions': f"Based on your shopping history, we found {len(items)} items you might need."
        }
    
    def _get_general_recommendations(self, pattern: UserPattern) -> List[str]:
        """Get general shopping recommendations"""
        recommendations = []
        
        # Analyze category balance
        top_category = max(pattern.category_preferences, key=pattern.category_preferences.get)
        recommendations.append(f"You frequently shop in {top_category} category")
        
        # Seasonal recommendations
        current_month = datetime.now().strftime('%B')
        if current_month in pattern.seasonal_patterns:
            recommendations.append(f"Consider seasonal {current_month} items")
        
        return recommendations
    
    def _item_to_dict(self, item: ShoppingItem) -> Dict:
        """Convert ShoppingItem to dictionary"""
        return {
            'name': item.name,
            'category': item.category,
            'brand': item.brand,
            'price': item.price,
            'quantity': item.quantity,
            'unit': item.unit,
            'priority_score': round(item.priority_score, 2),
            'confidence': round(item.confidence, 2),
            'reason': item.reason
        }
    
    def _load_models(self):
        """Load any existing ML models"""
        # Placeholder for loading pre-trained models
        pass
    
    def _save_models(self):
        """Save ML models"""
        # Placeholder for saving models
        pass

# Example usage and testing
if __name__ == "__main__":
    # Create AI Shopping Service
    ai_service = AIShoppingService()
    
    # Sample data for testing
    sample_inventory = [
        {'name': 'milk', 'quantity': '1', 'category': 'dairy', 'daysLeft': 2},
        {'name': 'bread', 'quantity': '0.5', 'category': 'grains', 'daysLeft': 1},
        {'name': 'apple', 'quantity': '3', 'category': 'fruits', 'daysLeft': 5}
    ]
    
    sample_history = [
        {
            'date': '2025-09-01',
            'items': [
                {'name': 'milk', 'category': 'dairy'},
                {'name': 'bread', 'category': 'grains'},
                {'name': 'chicken', 'category': 'meat'}
            ],
            'total_cost': 25.50
        },
        {
            'date': '2025-09-15',
            'items': [
                {'name': 'milk', 'category': 'dairy'},
                {'name': 'apple', 'category': 'fruits'},
                {'name': 'yogurt', 'category': 'dairy'}
            ],
            'total_cost': 18.75
        }
    ]
    
    # Generate smart shopping list
    result = ai_service.generate_smart_shopping_list(
        user_id="test_user",
        current_inventory=sample_inventory,
        shopping_history=sample_history,
        budget_limit=50.0
    )
    
    print("AI Shopping List Result:")
    print(json.dumps(result, indent=2))