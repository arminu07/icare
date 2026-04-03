#!/usr/bin/env python
"""
Test script to verify that multiple high-risk disease predictions are properly captured
for a single patient CSV upload
"""

import os
import sys

# Add the parent directory to path so we can import Icare module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Icare.settings')
django.setup()

# Now we can import from our app
from app.disease_predictor import predict_from_csv
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def test_single_patient_multiple_high_risk():
    """
    Test case: Upload a single patient CSV with multiple high-risk diseases
    Expected: All high-risk diseases should be counted and displayed
    """
    
    print("\n" + "="*80)
    print("TEST: Single Patient with Multiple High-Risk Diseases")
    print("="*80 + "\n")
    
    # Simulate a patient CSV row with high metabolic and cardiovascular markers
    # This should trigger multiple high-risk predictions
    test_data = [
        {
            'age': '65',              # Higher age = higher risk
            'gender': 'M',
            'blood_pressure': '160/100',  # Very high BP = Hypertension + Stroke risk high
            'cholesterol': '280',         # Very high = Heart disease + Stroke high
            'glucose': '180'              # Very high = Diabetes high
        }
    ]
    
    print("INPUT DATA:")
    print(f"  Patient age: {test_data[0]['age']}")
    print(f"  Blood pressure: {test_data[0]['blood_pressure']}")
    print(f"  Cholesterol: {test_data[0]['cholesterol']}")
    print(f"  Glucose: {test_data[0]['glucose']}")
    print()
    
    # Run prediction
    results = predict_from_csv(test_data)
    
    print("PREDICTION RESULTS:")
    print(f"  Total diseases analyzed: {results['total_diseases']}")
    print(f"  High-risk diseases: {results['high_risk_count']}")
    print(f"  Medium-risk diseases: {results['medium_risk_count']}")
    print(f"  Low-risk diseases: {results['low_risk_count']}")
    print(f"  Average confidence: {results['avg_confidence']}%")
    print()
    
    # Display all high-risk predictions
    high_risk_predictions = [p for p in results['predictions'] if p['risk'] == 'High']
    
    print(f"HIGH-RISK DISEASES ({len(high_risk_predictions)}):")
    for i, pred in enumerate(high_risk_predictions, 1):
        print(f"  {i}. {pred['disease']:<25} - {pred['confidence']:>3}% confidence")
    print()
    
    # Display other predictions
    other_predictions = [p for p in results['predictions'] if p['risk'] != 'High']
    print(f"OTHER DISEASES ({len(other_predictions)}):")
    for i, pred in enumerate(other_predictions[:10], 1):  # Show first 10
        print(f"  {i}. {pred['disease']:<25} - {pred['confidence']:>3}% ({pred['risk']})")
    if len(other_predictions) > 10:
        print(f"  ... and {len(other_predictions) - 10} more")
    print()
    
    # Validation checks
    print("VALIDATION CHECKS:")
    
    # Check 1: Risk count sum
    total_count = results['high_risk_count'] + results['medium_risk_count'] + results['low_risk_count']
    check1_pass = total_count == results['total_diseases']
    print(f"  ✓ Risk count sum: {total_count} == {results['total_diseases']} → {'PASS' if check1_pass else 'FAIL'}")
    
    # Check 2: At least 2 high-risk diseases expected
    check2_pass = results['high_risk_count'] >= 2
    print(f"  ✓ Multiple high-risk diseases: {results['high_risk_count']} >= 2 → {'PASS' if check2_pass else 'FAIL'}")
    
    # Check 3: Predictions are sorted by confidence (descending)
    confidences = [p['confidence'] for p in results['predictions']]
    is_sorted = all(confidences[i] >= confidences[i+1] for i in range(len(confidences)-1))
    print(f"  ✓ Predictions sorted by confidence: {'PASS' if is_sorted else 'FAIL'}")
    
    # Check 4: No duplicates
    disease_names = [p['disease'] for p in results['predictions']]
    has_duplicates = len(disease_names) != len(set(disease_names))
    print(f"  ✓ No duplicate diseases: {'PASS' if not has_duplicates else 'FAIL'}")
    
    print()
    overall_pass = check1_pass and check2_pass and is_sorted and not has_duplicates
    print("="*80)
    print(f"OVERALL: {'✓ ALL TESTS PASSED' if overall_pass else '✗ SOME TESTS FAILED'}")
    print("="*80 + "\n")
    
    return overall_pass


def test_multiple_patients():
    """
    Test case: Upload CSV with multiple patients
    Expected: Predictions should be aggregated with highest risk preserved
    """
    
    print("\n" + "="*80)
    print("TEST: Multiple Patients - Aggregation")
    print("="*80 + "\n")
    
    # Two patients with different risk profiles
    test_data = [
        {
            'age': '35',
            'gender': 'F',
            'blood_pressure': '110/70',
            'cholesterol': '150',
            'glucose': '85'
        },
        {
            'age': '70',
            'gender': 'M',
            'blood_pressure': '170/110',
            'cholesterol': '320',
            'glucose': '200'
        }
    ]
    
    print("INPUT DATA:")
    print(f"  Patient 1 (age 35, low risk markers)")
    print(f"  Patient 2 (age 70, high risk markers)")
    print()
    
    # Run prediction
    results = predict_from_csv(test_data)
    
    print("AGGREGATED RESULTS:")
    print(f"  Total diseases analyzed: {results['total_diseases']}")
    print(f"  High-risk diseases: {results['high_risk_count']}")
    print(f"  Medium-risk diseases: {results['medium_risk_count']}")
    print(f"  Average confidence: {results['avg_confidence']}%")
    print()
    
    # Validation
    total_count = results['high_risk_count'] + results['medium_risk_count'] + results['low_risk_count']
    check_pass = total_count == results['total_diseases']
    print(f"VALIDATION: Risk count sum check → {'PASS' if check_pass else 'FAIL'}")
    print("="*80 + "\n")
    
    return check_pass


if __name__ == '__main__':
    try:
        test1_pass = test_single_patient_multiple_high_risk()
        test2_pass = test_multiple_patients()
        
        if test1_pass and test2_pass:
            print("\n✓ ALL TESTS PASSED - Fix is working correctly!")
            sys.exit(0)
        else:
            print("\n✗ SOME TESTS FAILED - Please review the output above")
            sys.exit(1)
    except Exception as e:
        print(f"\n✗ ERROR during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
