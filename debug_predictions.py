#!/usr/bin/env python
"""
Debug script to test the actual prediction output
"""

import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Icare.settings')
django.setup()

from app.disease_predictor import predict_from_csv
import json

# Create test data with 3 patients
test_csv_data = [
    {
        'age': '65',
        'gender': 'M',
        'blood_pressure': '160/100',
        'cholesterol': '280',
        'glucose': '180'
    },
    {
        'age': '65',
        'gender': 'M',
        'blood_pressure': '160/100',
        'cholesterol': '280',
        'glucose': '180'
    },
    {
        'age': '65',
        'gender': 'M',
        'blood_pressure': '160/100',
        'cholesterol': '280',
        'glucose': '180'
    }
]

print("\n" + "="*80)
print("DEBUG TEST: Testing predict_from_csv with 3 patients")
print("="*80 + "\n")

print("Input: 3 patients with identical high-risk profile\n")

try:
    results = predict_from_csv(test_csv_data)
    
    print("\nRESULTS:")
    print(f"  Total Patients: {results.get('total_patients', 'N/A')}")
    print(f"  High Risk Instances: {results.get('high_risk_count', 'N/A')}")
    print(f"  Medium Risk Instances: {results.get('medium_risk_count', 'N/A')}")
    print(f"  Low Risk Instances: {results.get('low_risk_count', 'N/A')}")
    print(f"  Unique Diseases: {results.get('total_diseases', 'N/A')}")
    print(f"\n  Unique High Risk Diseases: {results.get('unique_high_risk', 'N/A')}")
    print(f"  Unique Medium Risk Diseases: {results.get('unique_medium_risk', 'N/A')}")
    print(f"  Unique Low Risk Diseases: {results.get('unique_low_risk', 'N/A')}")
    
    print("\n\nExpected Results:")
    print("  High Risk Instances: Should be ~6 (3 patients × 2 high-risk diseases)")
    print("  Medium Risk Instances: Should be ~3 (3 patients × 1 medium-risk disease)")
    print("  Total Instances: Should be ~9 (3 patients × 3 diseases)")
    
    print("\n\nActual vs Expected:")
    high_expected = 6
    medium_expected = 3
    high_actual = results.get('high_risk_count', 0)
    medium_actual = results.get('medium_risk_count', 0)
    
    if high_actual >= high_expected:
        print(f"  ✅ High Risk Count: {high_actual} >= {high_expected}")
    else:
        print(f"  ❌ High Risk Count: {high_actual} < {high_expected} (WRONG!)")
    
    if medium_actual >= medium_expected:
        print(f"  ✅ Medium Risk Count: {medium_actual} >= {medium_expected}")
    else:
        print(f"  ❌ Medium Risk Count: {medium_actual} < {medium_expected} (WRONG!)")
        
    print("\n\nFull Results Object:")
    print(json.dumps({k: v for k, v in results.items() if k != 'predictions'}, indent=2))
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
