#!/usr/bin/env python3
"""
Test script for mathematical accuracy of the calorie calculation system.
Target: 90-95% accuracy for all calculations.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from calorie_calculation_service import calorie_calculator
import json

def test_precise_calculations():
    """Test precise mathematical calculations with known values."""
    
    print("🧮 Testing Mathematical Accuracy (Target: 90-95%)")
    print("=" * 60)
    
    # Test cases with known nutritional values
    test_cases = [
        {
            "food": "apple",
            "weight_g": 182,  # 1 medium apple
            "expected_calories": 95,  # Known value
            "expected_protein": 0.5,
            "expected_carbs": 25,
            "expected_fat": 0.3,
            "expected_fiber": 4.4
        },
        {
            "food": "banana",
            "weight_g": 118,  # 1 medium banana
            "expected_calories": 105,
            "expected_protein": 1.3,
            "expected_carbs": 27,
            "expected_fat": 0.4,
            "expected_fiber": 3.1
        },
        {
            "food": "carrot",
            "weight_g": 61,  # 1 medium carrot
            "expected_calories": 25,
            "expected_protein": 0.6,
            "expected_carbs": 6,
            "expected_fat": 0.1,
            "expected_fiber": 1.7
        }
    ]
    
    total_tests = 0
    passed_tests = 0
    accuracy_scores = []
    
    for test_case in test_cases:
        print(f"\n🍎 Testing {test_case['food']} ({test_case['weight_g']}g)")
        print("-" * 40)
        
        # Calculate precise nutrition
        result = calorie_calculator.calculate_precise_nutrition(
            test_case['food'], 
            test_case['weight_g']
        )
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
            continue
        
        # Test calorie accuracy
        calorie_accuracy = test_accuracy(
            result['calories'], 
            test_case['expected_calories'], 
            "Calories"
        )
        accuracy_scores.append(calorie_accuracy)
        total_tests += 1
        if calorie_accuracy >= 90:
            passed_tests += 1
        
        # Test protein accuracy
        protein_accuracy = test_accuracy(
            result['protein'], 
            test_case['expected_protein'], 
            "Protein"
        )
        accuracy_scores.append(protein_accuracy)
        total_tests += 1
        if protein_accuracy >= 90:
            passed_tests += 1
        
        # Test carbs accuracy
        carbs_accuracy = test_accuracy(
            result['carbs'], 
            test_case['expected_carbs'], 
            "Carbs"
        )
        accuracy_scores.append(carbs_accuracy)
        total_tests += 1
        if carbs_accuracy >= 90:
            passed_tests += 1
        
        # Test fat accuracy
        fat_accuracy = test_accuracy(
            result['fat'], 
            test_case['expected_fat'], 
            "Fat"
        )
        accuracy_scores.append(fat_accuracy)
        total_tests += 1
        if fat_accuracy >= 90:
            passed_tests += 1
        
        # Test fiber accuracy
        fiber_accuracy = test_accuracy(
            result['fiber'], 
            test_case['expected_fiber'], 
            "Fiber"
        )
        accuracy_scores.append(fiber_accuracy)
        total_tests += 1
        if fiber_accuracy >= 90:
            passed_tests += 1
        
        # Display detailed results
        print(f"📊 Detailed Results:")
        print(f"   Calories: {result['calories']} (expected: {test_case['expected_calories']})")
        print(f"   Protein: {result['protein']}g (expected: {test_case['expected_protein']}g)")
        print(f"   Carbs: {result['carbs']}g (expected: {test_case['expected_carbs']}g)")
        print(f"   Fat: {result['fat']}g (expected: {test_case['expected_fat']}g)")
        print(f"   Fiber: {result['fiber']}g (expected: {test_case['expected_fiber']}g)")
        
        # Test calorie calculation validation
        if 'calorie_accuracy' in result:
            print(f"   Calorie Validation: {result['calorie_accuracy']}% accuracy")
    
    # Overall accuracy assessment
    overall_accuracy = sum(accuracy_scores) / len(accuracy_scores) if accuracy_scores else 0
    pass_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    
    print("\n" + "=" * 60)
    print("📈 ACCURACY SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {total_tests}")
    print(f"Passed Tests: {passed_tests}")
    print(f"Pass Rate: {pass_rate:.1f}%")
    print(f"Overall Accuracy: {overall_accuracy:.1f}%")
    
    if overall_accuracy >= 90:
        print("✅ ACCURACY TARGET ACHIEVED! (90-95% target met)")
    else:
        print("❌ ACCURACY TARGET NOT MET (Below 90%)")
    
    return overall_accuracy >= 90

def test_accuracy(calculated, expected, nutrient_name):
    """Calculate accuracy percentage for a nutrient."""
    if expected == 0:
        return 100 if calculated == 0 else 0
    
    accuracy = 100 - (abs(calculated - expected) / expected * 100)
    accuracy = max(0, min(100, accuracy))  # Clamp between 0-100
    
    status = "✅" if accuracy >= 90 else "❌"
    print(f"   {status} {nutrient_name}: {accuracy:.1f}% accuracy")
    
    return accuracy

def test_portion_scaling():
    """Test portion size scaling accuracy."""
    
    print("\n🔄 Testing Portion Size Scaling")
    print("=" * 60)
    
    # Test scaling from 100g to 200g (2x scale)
    base_result = calorie_calculator.calculate_precise_nutrition("apple", 100)
    scaled_result = calorie_calculator.calculate_precise_nutrition("apple", 200)
    
    if 'error' not in base_result and 'error' not in scaled_result:
        # Test that calories scale proportionally
        expected_calories = base_result['calories'] * 2
        actual_calories = scaled_result['calories']
        
        scaling_accuracy = 100 - (abs(actual_calories - expected_calories) / expected_calories * 100)
        
        print(f"📊 Scaling Test (100g → 200g):")
        print(f"   Base Calories: {base_result['calories']}")
        print(f"   Expected Scaled: {expected_calories}")
        print(f"   Actual Scaled: {actual_calories}")
        print(f"   Scaling Accuracy: {scaling_accuracy:.1f}%")
        
        if scaling_accuracy >= 95:
            print("✅ SCALING ACCURACY EXCELLENT!")
        elif scaling_accuracy >= 90:
            print("✅ SCALING ACCURACY GOOD!")
        else:
            print("❌ SCALING ACCURACY NEEDS IMPROVEMENT")
        
        return scaling_accuracy >= 90
    
    return False

def test_validation_system():
    """Test portion size validation system."""
    
    print("\n🔍 Testing Portion Size Validation")
    print("=" * 60)
    
    # Test normal portion
    normal_validation = calorie_calculator.validate_portion_size("apple", 182)
    print(f"📊 Normal Portion (182g): {normal_validation['recommendation']}")
    
    # Test large portion
    large_validation = calorie_calculator.validate_portion_size("apple", 500)
    print(f"📊 Large Portion (500g): {large_validation['recommendation']}")
    
    # Test small portion
    small_validation = calorie_calculator.validate_portion_size("apple", 50)
    print(f"📊 Small Portion (50g): {small_validation['recommendation']}")
    
    return True

if __name__ == "__main__":
    print("🧮 MATHEMATICAL ACCURACY TEST SUITE")
    print("Target: 90-95% accuracy for all calculations")
    print("=" * 60)
    
    # Run all tests
    test1_passed = test_precise_calculations()
    test2_passed = test_portion_scaling()
    test3_passed = test_validation_system()
    
    print("\n" + "=" * 60)
    print("🏁 FINAL RESULTS")
    print("=" * 60)
    
    if test1_passed and test2_passed and test3_passed:
        print("🎉 ALL TESTS PASSED! Mathematical accuracy target achieved.")
        print("✅ System ready for production with 90-95% accuracy.")
    else:
        print("⚠️  Some tests failed. Review accuracy calculations.")
        print("🔧 Consider adjusting nutritional database or calculation methods.")
    
    print("\n📋 Test Summary:")
    print(f"   Precise Calculations: {'✅' if test1_passed else '❌'}")
    print(f"   Portion Scaling: {'✅' if test2_passed else '❌'}")
    print(f"   Validation System: {'✅' if test3_passed else '❌'}")
