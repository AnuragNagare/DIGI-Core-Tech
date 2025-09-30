#!/usr/bin/env python3
"""
AI Meal Generator Service
Uses machine learning to learn user preferences and generate personalized meal plans
"""

import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import pickle
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
import pandas as pd

@dataclass
class UserPreference:
    """User preference data structure"""
    user_id: str
    dietary_restrictions: List[str] = None
    favorite_ingredients: List[str] = None
    disliked_ingredients: List[str] = None
    preferred_cuisines: List[str] = None
    meal_frequency: Dict[str, int] = None  # breakfast, lunch, dinner, snack
    cooking_skill: str = "intermediate"  # beginner, intermediate, advanced
    time_constraints: Dict[str, int] = None  # max cooking time per meal type
    health_goals: List[str] = None  # weight_loss, muscle_gain, maintenance, etc.
    budget_range: str = "medium"  # low, medium, high
    family_size: int = 1
    
    def __post_init__(self):
        if self.dietary_restrictions is None:
            self.dietary_restrictions = []
        if self.favorite_ingredients is None:
            self.favorite_ingredients = []
        if self.disliked_ingredients is None:
            self.disliked_ingredients = []
        if self.preferred_cuisines is None:
            self.preferred_cuisines = []
        if self.meal_frequency is None:
            self.meal_frequency = {"breakfast": 7, "lunch": 7, "dinner": 7, "snack": 3}
        if self.time_constraints is None:
            self.time_constraints = {"breakfast": 15, "lunch": 30, "dinner": 45, "snack": 10}
        if self.health_goals is None:
            self.health_goals = ["maintenance"]

@dataclass
class MealRecord:
    """Individual meal consumption record"""
    user_id: str
    meal_name: str
    ingredients: List[str]
    meal_type: str  # breakfast, lunch, dinner, snack
    date: str
    rating: Optional[float] = None  # 1-5 stars if provided
    prep_time: Optional[int] = None
    cost: Optional[float] = None
    calories: Optional[int] = None
    enjoyed: Optional[bool] = None  # did they finish it?
    
@dataclass
class GeneratedMeal:
    """Generated meal suggestion"""
    meal_id: str
    name: str
    ingredients: List[str]
    instructions: List[str]
    meal_type: str
    estimated_prep_time: int
    estimated_cost: float
    estimated_calories: int
    confidence_score: float
    reasoning: str
    dietary_labels: List[str]
    cuisine: str
    difficulty: str

class AIPersonalizationEngine:
    """Core AI engine for learning user preferences and generating personalized meals"""
    
    def __init__(self, data_dir: str = "ai_meal_data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        # ML Models
        self.ingredient_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.meal_clusterer = KMeans(n_clusters=10, random_state=42)
        
        # User data storage
        self.user_preferences: Dict[str, UserPreference] = {}
        self.meal_history: Dict[str, List[MealRecord]] = defaultdict(list)
        self.ingredient_preferences: Dict[str, Dict[str, float]] = defaultdict(dict)
        
        # Load existing data
        self._load_user_data()
        
    def _load_user_data(self):
        """Load existing user preference data"""
        try:
            prefs_file = os.path.join(self.data_dir, "user_preferences.json")
            if os.path.exists(prefs_file):
                with open(prefs_file, 'r') as f:
                    data = json.load(f)
                    for user_id, pref_data in data.items():
                        self.user_preferences[user_id] = UserPreference(**pref_data)
            
            history_file = os.path.join(self.data_dir, "meal_history.json")
            if os.path.exists(history_file):
                with open(history_file, 'r') as f:
                    data = json.load(f)
                    for user_id, meals in data.items():
                        self.meal_history[user_id] = [MealRecord(**meal) for meal in meals]
                        
        except Exception as e:
            print(f"Error loading user data: {e}")
    
    def _save_user_data(self):
        """Save user preference data"""
        try:
            prefs_file = os.path.join(self.data_dir, "user_preferences.json")
            with open(prefs_file, 'w') as f:
                data = {user_id: asdict(pref) for user_id, pref in self.user_preferences.items()}
                json.dump(data, f, indent=2)
            
            history_file = os.path.join(self.data_dir, "meal_history.json")
            with open(history_file, 'w') as f:
                data = {user_id: [asdict(meal) for meal in meals] 
                       for user_id, meals in self.meal_history.items()}
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"Error saving user data: {e}")
    
    def learn_from_meal(self, meal_record: MealRecord):
        """Learn from a user's meal consumption"""
        user_id = meal_record.user_id
        
        # Add to meal history
        self.meal_history[user_id].append(meal_record)
        
        # Update ingredient preferences based on rating/enjoyment
        if meal_record.rating is not None or meal_record.enjoyed is not None:
            preference_score = 0.0
            
            if meal_record.rating:
                preference_score = (meal_record.rating - 3.0) / 2.0  # Convert 1-5 to -1 to 1
            elif meal_record.enjoyed is not None:
                preference_score = 1.0 if meal_record.enjoyed else -0.5
            
            # Update ingredient preferences
            for ingredient in meal_record.ingredients:
                if ingredient not in self.ingredient_preferences[user_id]:
                    self.ingredient_preferences[user_id][ingredient] = 0.0
                
                # Apply learning rate decay
                current_pref = self.ingredient_preferences[user_id][ingredient]
                learning_rate = 0.1
                self.ingredient_preferences[user_id][ingredient] = (
                    current_pref + learning_rate * (preference_score - current_pref)
                )
        
        # Update user preferences based on patterns
        self._update_user_preferences(user_id)
        
        # Save updated data
        self._save_user_data()
    
    def _update_user_preferences(self, user_id: str):
        """Update user preferences based on meal history patterns"""
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = UserPreference(user_id=user_id)
        
        user_meals = self.meal_history[user_id]
        if len(user_meals) < 5:  # Need enough data to learn patterns
            return
        
        # Analyze favorite ingredients (top rated/enjoyed)
        ingredient_scores = defaultdict(list)
        for meal in user_meals[-50:]:  # Last 50 meals
            if meal.rating and meal.rating >= 4:
                for ingredient in meal.ingredients:
                    ingredient_scores[ingredient].append(meal.rating)
        
        # Update favorite ingredients
        avg_scores = {ing: np.mean(scores) for ing, scores in ingredient_scores.items()}
        top_ingredients = sorted(avg_scores.items(), key=lambda x: x[1], reverse=True)[:15]
        self.user_preferences[user_id].favorite_ingredients = [ing for ing, _ in top_ingredients]
        
        # Analyze meal timing patterns
        meal_type_counts = Counter(meal.meal_type for meal in user_meals[-30:])
        self.user_preferences[user_id].meal_frequency = dict(meal_type_counts)
        
        # Analyze cooking time preferences
        time_prefs = defaultdict(list)
        for meal in user_meals[-20:]:
            if meal.prep_time and meal.rating and meal.rating >= 4:
                time_prefs[meal.meal_type].append(meal.prep_time)
        
        for meal_type, times in time_prefs.items():
            if times:
                avg_time = int(np.mean(times))
                self.user_preferences[user_id].time_constraints[meal_type] = avg_time
    
    def generate_personalized_meals(self, 
                                   user_id: str,
                                   days: int = 7,
                                   meals_per_day: int = 3,
                                   available_ingredients: List[str] = None) -> List[GeneratedMeal]:
        """Generate personalized meal suggestions using AI"""
        
        if user_id not in self.user_preferences:
            # Create default preferences for new user
            self.user_preferences[user_id] = UserPreference(user_id=user_id)
        
        user_prefs = self.user_preferences[user_id]
        user_ingredient_prefs = self.ingredient_preferences.get(user_id, {})
        
        # Load meal database (this would be expanded with real recipe data)
        meal_database = self._load_meal_database()
        
        # Generate meals using multiple AI strategies
        generated_meals = []
        
        meal_types = ['breakfast', 'lunch', 'dinner']
        if meals_per_day > 3:
            meal_types.append('snack')
        
        for day in range(days):
            for meal_type in meal_types:
                meal = self._generate_single_meal(
                    user_prefs, 
                    user_ingredient_prefs,
                    meal_type,
                    available_ingredients or [],
                    meal_database,
                    day
                )
                if meal:
                    generated_meals.append(meal)
        
        return generated_meals
    
    def _generate_single_meal(self,
                             user_prefs: UserPreference,
                             ingredient_prefs: Dict[str, float],
                             meal_type: str,
                             available_ingredients: List[str],
                             meal_database: List[Dict],
                             day_offset: int) -> Optional[GeneratedMeal]:
        """Generate a single personalized meal"""
        
        # Score meals based on user preferences
        scored_meals = []
        
        for meal_data in meal_database:
            if meal_data.get('meal_type') != meal_type:
                continue
            
            score = self._calculate_meal_score(
                meal_data, user_prefs, ingredient_prefs, available_ingredients
            )
            
            if score > 0.3:  # Minimum confidence threshold
                scored_meals.append((meal_data, score))
        
        # Sort by score and add some randomness to prevent repetition
        scored_meals.sort(key=lambda x: x[1] + np.random.normal(0, 0.1), reverse=True)
        
        if not scored_meals:
            return None
        
        # Select best meal
        best_meal_data, confidence = scored_meals[0]
        
        # Generate reasoning
        reasoning_parts = []
        if any(ing in ingredient_prefs for ing in best_meal_data['ingredients']):
            reasoning_parts.append("Contains your favorite ingredients")
        if best_meal_data['prep_time'] <= user_prefs.time_constraints.get(meal_type, 60):
            reasoning_parts.append("Fits your time constraints")
        if any(ing in available_ingredients for ing in best_meal_data['ingredients']):
            reasoning_parts.append("Uses ingredients you have available")
        
        reasoning = "; ".join(reasoning_parts) if reasoning_parts else "Good nutritional balance"
        
        return GeneratedMeal(
            meal_id=f"{user_prefs.user_id}_{meal_type}_{day_offset}_{datetime.now().strftime('%Y%m%d')}",
            name=best_meal_data['name'],
            ingredients=best_meal_data['ingredients'],
            instructions=best_meal_data.get('instructions', []),
            meal_type=meal_type,
            estimated_prep_time=best_meal_data['prep_time'],
            estimated_cost=best_meal_data.get('cost', 5.0),
            estimated_calories=best_meal_data.get('calories', 400),
            confidence_score=confidence,
            reasoning=reasoning,
            dietary_labels=best_meal_data.get('dietary_labels', []),
            cuisine=best_meal_data.get('cuisine', 'International'),
            difficulty=best_meal_data.get('difficulty', 'intermediate')
        )
    
    def _calculate_meal_score(self,
                             meal_data: Dict,
                             user_prefs: UserPreference,
                             ingredient_prefs: Dict[str, float],
                             available_ingredients: List[str]) -> float:
        """Calculate how well a meal matches user preferences"""
        
        score = 0.5  # Base score
        
        # Ingredient preference scoring
        ingredient_score = 0.0
        for ingredient in meal_data['ingredients']:
            if ingredient in ingredient_prefs:
                ingredient_score += ingredient_prefs[ingredient]
            if ingredient in user_prefs.favorite_ingredients:
                ingredient_score += 0.3
            if ingredient in user_prefs.disliked_ingredients:
                ingredient_score -= 0.5
            if ingredient in available_ingredients:
                ingredient_score += 0.2  # Bonus for using available ingredients
        
        score += ingredient_score / len(meal_data['ingredients'])
        
        # Dietary restrictions
        meal_labels = set(meal_data.get('dietary_labels', []))
        user_restrictions = set(user_prefs.dietary_restrictions)
        
        # Check if meal violates any dietary restrictions
        if user_restrictions:
            compatible_restrictions = meal_labels.intersection(user_restrictions)
            if compatible_restrictions:
                score += 0.3
            else:
                # Check for violations
                violation_map = {
                    'vegetarian': ['meat', 'chicken', 'beef', 'pork', 'fish'],
                    'vegan': ['meat', 'chicken', 'beef', 'pork', 'fish', 'dairy', 'eggs'],
                    'gluten_free': ['wheat', 'bread', 'pasta', 'flour'],
                    'dairy_free': ['milk', 'cheese', 'butter', 'yogurt']
                }
                
                for restriction in user_restrictions:
                    if restriction in violation_map:
                        violation_ingredients = violation_map[restriction]
                        if any(ing.lower() in [i.lower() for i in meal_data['ingredients']] 
                              for ing in violation_ingredients):
                            score -= 0.8  # Heavy penalty for violations
        
        # Time constraints
        max_time = user_prefs.time_constraints.get(meal_data.get('meal_type', 'lunch'), 60)
        if meal_data.get('prep_time', 30) <= max_time:
            score += 0.2
        else:
            score -= 0.3
        
        # Cuisine preferences
        if meal_data.get('cuisine') in user_prefs.preferred_cuisines:
            score += 0.2
        
        # Cooking skill match
        difficulty_scores = {'beginner': 1, 'intermediate': 2, 'advanced': 3}
        user_skill = difficulty_scores.get(user_prefs.cooking_skill, 2)
        meal_difficulty = difficulty_scores.get(meal_data.get('difficulty', 'intermediate'), 2)
        
        if meal_difficulty <= user_skill:
            score += 0.1
        else:
            score -= 0.2
        
        # Health goals alignment
        if 'weight_loss' in user_prefs.health_goals:
            if meal_data.get('calories', 500) < 400:
                score += 0.2
        elif 'muscle_gain' in user_prefs.health_goals:
            if meal_data.get('protein', 0) > 20:
                score += 0.2
        
        return max(0.0, min(1.0, score))  # Clamp between 0 and 1
    
    def _load_meal_database(self) -> List[Dict]:
        """Load meal database (expandable with real recipes)"""
        
        # This would be replaced with a real recipe database
        sample_meals = [
            {
                "name": "Avocado Toast with Scrambled Eggs",
                "ingredients": ["bread", "avocado", "eggs", "salt", "pepper", "butter"],
                "meal_type": "breakfast",
                "prep_time": 10,
                "cost": 4.0,
                "calories": 350,
                "dietary_labels": ["vegetarian"],
                "cuisine": "American",
                "difficulty": "beginner",
                "protein": 15,
                "instructions": [
                    "Toast bread slices",
                    "Mash avocado with salt and pepper",
                    "Scramble eggs in butter",
                    "Spread avocado on toast, top with eggs"
                ]
            },
            {
                "name": "Greek Quinoa Bowl",
                "ingredients": ["quinoa", "cucumber", "tomato", "feta", "olives", "olive_oil", "lemon"],
                "meal_type": "lunch",
                "prep_time": 25,
                "cost": 6.0,
                "calories": 420,
                "dietary_labels": ["vegetarian", "gluten_free"],
                "cuisine": "Mediterranean",
                "difficulty": "intermediate",
                "protein": 18,
                "instructions": [
                    "Cook quinoa according to package instructions",
                    "Chop cucumber and tomato",
                    "Mix vegetables with quinoa",
                    "Top with feta and olives",
                    "Drizzle with olive oil and lemon"
                ]
            },
            {
                "name": "Grilled Chicken with Sweet Potato",
                "ingredients": ["chicken_breast", "sweet_potato", "broccoli", "olive_oil", "garlic", "herbs"],
                "meal_type": "dinner",
                "prep_time": 35,
                "cost": 8.0,
                "calories": 480,
                "dietary_labels": ["gluten_free", "dairy_free"],
                "cuisine": "American",
                "difficulty": "intermediate",
                "protein": 35,
                "instructions": [
                    "Season chicken with herbs and garlic",
                    "Grill chicken for 6-7 minutes per side",
                    "Roast sweet potato at 400°F for 25 minutes",
                    "Steam broccoli until tender",
                    "Serve together with olive oil drizzle"
                ]
            },
            {
                "name": "Berry Protein Smoothie",
                "ingredients": ["berries", "protein_powder", "banana", "almond_milk", "spinach", "chia_seeds"],
                "meal_type": "snack",
                "prep_time": 5,
                "cost": 3.0,
                "calories": 280,
                "dietary_labels": ["vegan", "gluten_free"],
                "cuisine": "Health",
                "difficulty": "beginner",
                "protein": 25,
                "instructions": [
                    "Add all ingredients to blender",
                    "Blend until smooth",
                    "Adjust consistency with more almond milk if needed",
                    "Serve immediately"
                ]
            },
            {
                "name": "Vegetarian Stir Fry",
                "ingredients": ["tofu", "bell_peppers", "broccoli", "carrots", "soy_sauce", "ginger", "garlic", "rice"],
                "meal_type": "dinner",
                "prep_time": 20,
                "cost": 5.5,
                "calories": 380,
                "dietary_labels": ["vegetarian", "vegan"],
                "cuisine": "Asian",
                "difficulty": "intermediate",
                "protein": 20,
                "instructions": [
                    "Press and cube tofu",
                    "Cook rice according to package instructions",
                    "Heat oil in wok, add tofu and cook until golden",
                    "Add vegetables and stir fry for 5-7 minutes",
                    "Add sauce and serve over rice"
                ]
            }
        ]
        
        return sample_meals
    
    def optimize_for_waste_reduction(self, 
                                   user_id: str,
                                   expiring_ingredients: List[Dict]) -> List[GeneratedMeal]:
        """Generate meals that use expiring ingredients to reduce waste"""
        
        expiring_items = [item['name'].lower() for item in expiring_ingredients]
        
        # Generate meals prioritizing expiring ingredients
        waste_reducing_meals = self.generate_personalized_meals(
            user_id=user_id,
            days=3,  # Focus on next few days
            available_ingredients=expiring_items
        )
        
        # Filter and re-score based on waste reduction potential
        optimized_meals = []
        for meal in waste_reducing_meals:
            waste_reduction_score = 0
            ingredients_used = 0
            
            for ingredient in meal.ingredients:
                if ingredient.lower() in expiring_items:
                    ingredients_used += 1
                    
                    # Find expiry info
                    for item in expiring_ingredients:
                        if item['name'].lower() == ingredient.lower():
                            days_left = item.get('days_left', 0)
                            if days_left <= 2:
                                waste_reduction_score += 0.5
                            elif days_left <= 5:
                                waste_reduction_score += 0.3
            
            if ingredients_used > 0:
                # Update meal reasoning
                meal.reasoning += f" | Uses {ingredients_used} expiring ingredients"
                meal.confidence_score += waste_reduction_score * 0.2
                optimized_meals.append(meal)
        
        return optimized_meals
    
    def get_user_insights(self, user_id: str) -> Dict[str, Any]:
        """Generate insights about user's eating patterns and preferences"""
        
        if user_id not in self.meal_history:
            return {"message": "Not enough data for insights"}
        
        user_meals = self.meal_history[user_id]
        user_prefs = self.user_preferences.get(user_id)
        
        insights = {
            "total_meals_tracked": len(user_meals),
            "favorite_meal_type": Counter(meal.meal_type for meal in user_meals).most_common(1)[0][0],
            "average_rating": np.mean([meal.rating for meal in user_meals if meal.rating]),
            "most_used_ingredients": Counter([ing for meal in user_meals for ing in meal.ingredients]).most_common(10),
            "preferred_cuisines": user_prefs.preferred_cuisines if user_prefs else [],
            "dietary_adherence": self._calculate_dietary_adherence(user_meals, user_prefs),
            "cooking_time_analysis": self._analyze_cooking_times(user_meals),
            "recommendations": self._generate_improvement_recommendations(user_id)
        }
        
        return insights
    
    def _calculate_dietary_adherence(self, meals: List[MealRecord], prefs: UserPreference) -> Dict:
        """Calculate how well user adheres to their dietary restrictions"""
        if not prefs or not prefs.dietary_restrictions:
            return {"adherence_rate": 100, "violations": []}
        
        violations = []
        # This would implement dietary adherence checking
        return {"adherence_rate": 95, "violations": violations}
    
    def _analyze_cooking_times(self, meals: List[MealRecord]) -> Dict:
        """Analyze user's cooking time patterns"""
        times_by_type = defaultdict(list)
        
        for meal in meals:
            if meal.prep_time:
                times_by_type[meal.meal_type].append(meal.prep_time)
        
        analysis = {}
        for meal_type, times in times_by_type.items():
            analysis[meal_type] = {
                "average_time": np.mean(times),
                "preferred_range": f"{min(times)}-{max(times)} minutes"
            }
        
        return analysis
    
    def _generate_improvement_recommendations(self, user_id: str) -> List[str]:
        """Generate personalized recommendations for improvement"""
        recommendations = []
        
        user_meals = self.meal_history[user_id]
        
        # Analyze patterns and suggest improvements
        if len(user_meals) > 10:
            meal_types = [meal.meal_type for meal in user_meals[-14:]]  # Last 2 weeks
            type_counts = Counter(meal_types)
            
            if type_counts.get('breakfast', 0) < 10:
                recommendations.append("Try to include breakfast more regularly for better nutrition balance")
            
            if type_counts.get('snack', 0) > 10:
                recommendations.append("Consider reducing snacks and focus on balanced main meals")
            
            # Check ingredient diversity
            all_ingredients = [ing for meal in user_meals[-20:] for ing in meal.ingredients]
            unique_ingredients = len(set(all_ingredients))
            
            if unique_ingredients < 30:
                recommendations.append("Try to diversify your ingredients for better nutrition")
        
        return recommendations

# Initialize global AI engine
ai_meal_engine = AIPersonalizationEngine()