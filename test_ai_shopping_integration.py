#!/usr/bin/env python3
"""
AI Shopping List System - Integration Test
Tests the complete ML-powered shopping list system with predictions, analytics, and smart suggestions.
"""

import requests
import json
import time
import sys
from typing import Dict, List, Any

class AIShoppingListTester:
    def __init__(self, base_url: str = "http://localhost:3000"):
        self.base_url = base_url
        self.ml_service_url = "http://localhost:8001"  # AI Shopping ML service
        self.user_id = "test-user-123"
        self.test_results = []
        
    def log_result(self, test_name: str, success: bool, message: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message
        })
    
    def test_ml_service_connection(self) -> bool:
        """Test connection to ML service"""
        try:
            response = requests.get(f"{self.ml_service_url}/health")
            if response.status_code == 200:
                self.log_result("ML Service Connection", True, "AI shopping service is running")
                return True
            else:
                self.log_result("ML Service Connection", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("ML Service Connection", False, f"Connection failed: {str(e)}")
            return False
    
    def test_ai_predictions(self) -> bool:
        """Test AI prediction functionality"""
        try:
            payload = {
                "user_id": self.user_id,
                "current_items": ["milk", "bread"],
                "budget": 100,
                "preferences": {
                    "dietary_restrictions": [],
                    "preferred_brands": ["organic"],
                    "shopping_frequency": "weekly"
                }
            }
            
            response = requests.post(
                f"{self.ml_service_url}/api/shopping/ai-predict",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                predictions = data.get("predictions", [])
                confidence = data.get("confidence_scores", {})
                
                if predictions and len(predictions) > 0:
                    self.log_result("AI Predictions", True, 
                                  f"Generated {len(predictions)} predictions with confidence scores")
                    print(f"   Sample predictions: {predictions[:3]}")
                    return True
                else:
                    self.log_result("AI Predictions", False, "No predictions generated")
                    return False
            else:
                self.log_result("AI Predictions", False, f"API error: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("AI Predictions", False, f"Error: {str(e)}")
            return False
    
    def test_pattern_analysis(self) -> bool:
        """Test user pattern analysis"""
        try:
            response = requests.get(f"{self.ml_service_url}/api/shopping/patterns/{self.user_id}")
            
            if response.status_code == 200:
                data = response.json()
                patterns = data.get("patterns", {})
                
                expected_keys = ["frequent_items", "category_preferences", "seasonal_trends"]
                if all(key in patterns for key in expected_keys):
                    self.log_result("Pattern Analysis", True, "All pattern types analyzed successfully")
                    return True
                else:
                    self.log_result("Pattern Analysis", False, "Missing pattern analysis data")
                    return False
            else:
                self.log_result("Pattern Analysis", False, f"API error: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Pattern Analysis", False, f"Error: {str(e)}")
            return False
    
    def test_smart_suggestions(self) -> bool:
        """Test smart suggestions API"""
        try:
            params = {
                "userId": self.user_id,
                "action": "suggestions",
                "month": "December",
                "budget": "150"
            }
            
            response = requests.get(f"{self.base_url}/api/shopping/ai", params=params)
            
            if response.status_code == 200:
                data = response.json()
                suggestions = data.get("suggestions", {})
                
                suggestion_types = ["seasonal", "budget", "trending", "frequent"]
                available_types = [t for t in suggestion_types if t in suggestions and suggestions[t]]
                
                if len(available_types) >= 2:
                    self.log_result("Smart Suggestions", True, 
                                  f"Generated {len(available_types)} types of suggestions")
                    return True
                else:
                    self.log_result("Smart Suggestions", False, "Insufficient suggestion types")
                    return False
            else:
                self.log_result("Smart Suggestions", False, f"API error: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Smart Suggestions", False, f"Error: {str(e)}")
            return False
    
    def test_shopping_analytics(self) -> bool:
        """Test shopping analytics"""
        try:
            params = {
                "userId": self.user_id,
                "action": "analytics",
                "range": "month"
            }
            
            response = requests.get(f"{self.base_url}/api/shopping/ai", params=params)
            
            if response.status_code == 200:
                data = response.json()
                metrics = data.get("metrics", {})
                
                required_metrics = ["totalSpent", "itemsBought", "categoryBreakdown", "spendingTrend"]
                if all(key in metrics for key in required_metrics):
                    self.log_result("Shopping Analytics", True, "All analytics metrics available")
                    print(f"   Total spent: ${metrics.get('totalSpent', 0):.2f}")
                    print(f"   Items bought: {metrics.get('itemsBought', 0)}")
                    return True
                else:
                    self.log_result("Shopping Analytics", False, "Missing analytics data")
                    return False
            else:
                self.log_result("Shopping Analytics", False, f"API error: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Shopping Analytics", False, f"Error: {str(e)}")
            return False
    
    def test_user_feedback(self) -> bool:
        """Test user feedback system"""
        try:
            feedback_data = {
                "userId": self.user_id,
                "action": "feedback",
                "data": {
                    "item": "organic milk",
                    "action": "accepted",
                    "rating": 5
                }
            }
            
            response = requests.post(
                f"{self.base_url}/api/shopping/ai",
                json=feedback_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_result("User Feedback", True, "Feedback stored successfully")
                    return True
                else:
                    self.log_result("User Feedback", False, "Feedback not processed")
                    return False
            else:
                self.log_result("User Feedback", False, f"API error: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("User Feedback", False, f"Error: {str(e)}")
            return False
    
    def test_seasonal_recommendations(self) -> bool:
        """Test seasonal recommendations"""
        try:
            response = requests.get(f"{self.ml_service_url}/api/shopping/seasonal/December")
            
            if response.status_code == 200:
                data = response.json()
                seasonal_items = data.get("seasonal_recommendations", [])
                
                if seasonal_items and len(seasonal_items) > 0:
                    self.log_result("Seasonal Recommendations", True, 
                                  f"Found {len(seasonal_items)} seasonal items")
                    print(f"   December items: {seasonal_items[:3]}")
                    return True
                else:
                    self.log_result("Seasonal Recommendations", False, "No seasonal items found")
                    return False
            else:
                self.log_result("Seasonal Recommendations", False, f"API error: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Seasonal Recommendations", False, f"Error: {str(e)}")
            return False
    
    def test_priority_scoring(self) -> bool:
        """Test intelligent priority scoring"""
        try:
            payload = {
                "user_id": self.user_id,
                "items": ["milk", "luxury chocolate", "toilet paper", "ice cream"],
                "budget": 50,
                "urgency_factors": ["essential", "want", "essential", "want"]
            }
            
            # Test through prediction API which includes priority scoring
            response = requests.post(
                f"{self.ml_service_url}/api/shopping/ai-predict",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                priorities = data.get("priority_scores", {})
                
                if priorities:
                    # Check if essentials get higher priority
                    milk_priority = priorities.get("milk", 0)
                    chocolate_priority = priorities.get("luxury chocolate", 0)
                    
                    if milk_priority > chocolate_priority:
                        self.log_result("Priority Scoring", True, 
                                      "Intelligent priority scoring working correctly")
                        return True
                    else:
                        self.log_result("Priority Scoring", False, "Priority scoring logic error")
                        return False
                else:
                    self.log_result("Priority Scoring", False, "No priority scores returned")
                    return False
            else:
                self.log_result("Priority Scoring", False, f"API error: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Priority Scoring", False, f"Error: {str(e)}")
            return False
    
    def test_integration_flow(self) -> bool:
        """Test complete integration flow"""
        try:
            print("\n🔄 Testing complete AI shopping flow...")
            
            # Step 1: Get AI predictions
            predictions_response = requests.get(
                f"{self.base_url}/api/shopping/ai",
                params={"userId": self.user_id, "action": "predictions", "currentItems": "milk,bread", "budget": "100"}
            )
            
            if predictions_response.status_code != 200:
                self.log_result("Integration Flow", False, "Failed to get predictions")
                return False
            
            # Step 2: Get smart suggestions
            suggestions_response = requests.get(
                f"{self.base_url}/api/shopping/ai",
                params={"userId": self.user_id, "action": "suggestions", "month": "December"}
            )
            
            if suggestions_response.status_code != 200:
                self.log_result("Integration Flow", False, "Failed to get suggestions")
                return False
            
            # Step 3: Submit feedback
            feedback_response = requests.post(
                f"{self.base_url}/api/shopping/ai",
                json={
                    "userId": self.user_id,
                    "action": "feedback",
                    "data": {"item": "milk", "action": "accepted", "rating": 5}
                }
            )
            
            if feedback_response.status_code != 200:
                self.log_result("Integration Flow", False, "Failed to submit feedback")
                return False
            
            # Step 4: Get analytics
            analytics_response = requests.get(
                f"{self.base_url}/api/shopping/ai",
                params={"userId": self.user_id, "action": "analytics", "range": "month"}
            )
            
            if analytics_response.status_code != 200:
                self.log_result("Integration Flow", False, "Failed to get analytics")
                return False
            
            self.log_result("Integration Flow", True, 
                          "Complete AI shopping flow working end-to-end")
            return True
            
        except Exception as e:
            self.log_result("Integration Flow", False, f"Integration error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all tests and provide summary"""
        print("🚀 Starting AI Shopping List System Integration Tests...")
        print("=" * 60)
        
        # Core ML service tests
        print("\n📊 Testing ML Service Components...")
        self.test_ml_service_connection()
        self.test_ai_predictions()
        self.test_pattern_analysis()
        self.test_seasonal_recommendations()
        self.test_priority_scoring()
        
        # API integration tests
        print("\n🌐 Testing API Integration...")
        self.test_smart_suggestions()
        self.test_shopping_analytics()
        self.test_user_feedback()
        
        # End-to-end test
        print("\n🔗 Testing Complete Integration...")
        self.test_integration_flow()
        
        # Results summary
        print("\n" + "=" * 60)
        print("📈 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        passed_tests = sum(1 for result in self.test_results if result["success"])
        total_tests = len(self.test_results)
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"✅ Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        if passed_tests == total_tests:
            print("🎉 All tests passed! AI Shopping List system is fully functional.")
            print("\n🚀 Key Features Validated:")
            print("   • AI-powered shopping predictions with ML")
            print("   • Smart suggestions (seasonal, budget, trending)")
            print("   • User pattern analysis and learning")
            print("   • Shopping analytics and insights")
            print("   • User feedback system for continuous improvement")
            print("   • Priority-based intelligent scoring")
            print("   • Complete end-to-end integration")
        else:
            print(f"❌ {total_tests - passed_tests} tests failed. Check the issues above.")
            
        return passed_tests == total_tests

def main():
    """Main test execution"""
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:3000"
    
    tester = AIShoppingListTester(base_url)
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()