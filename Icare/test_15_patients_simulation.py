#!/usr/bin/env python
"""
Comprehensive test to simulate 15 patients with 2 high-risk diseases each
This simulates the exact scenario reported by the user
"""
import os
import sys
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Icare.settings')
django.setup()

from app.disease_predictor import predict_from_csv
import logging

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_15_patients_debug.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create test data: 15 patients, each will likely have at least 2 high-risk diseases
test_data = []
for i in range(15):
    patient = {
        'age': str(65 + i),  # Ages 65-79
        'gender': 'M' if i % 2 == 0 else 'F',
        'blood_pressure': '150/95',  # High - triggers Hypertension
        'cholesterol': '280',  # High - triggers Heart Disease, Cholesterol issues
        'glucose': '150'  # High - triggers Diabetes
    }
    test_data.append(patient)

print("="*70)
print("TEST: 15 Patients with High-Risk Medical Readings")
print("="*70)
print(f"\nTest Data Created:")
print(f"  - Number of patients: {len(test_data)}")
print(f"  - Each patient has: BP=150/95, Cholesterol=280, Glucose=150")
print(f"  - Expected high-risk diseases per patient: ~3-5 (Diabetes, Hypertension, Heart Disease, etc.)")
print(f"  - Expected total instances for 15 patients: 45-75 high-risk diseases")

try:
    logger.info("Starting prediction for 15 patients...")
    results = predict_from_csv(test_data)
    
    print(f"\n{'='*70}")
    print("RESULTS FROM predict_from_csv:")
    print(f"{'='*70}")
    print(f"\n1. Instance Counts (what we're testing):")
    print(f"   - High-risk instances: {results['high_risk_count']}")
    print(f"   - Medium-risk instances: {results['medium_risk_count']}")
    print(f"   - Low-risk instances: {results['low_risk_count']}")
    print(f"   - Total instances: {results['high_risk_count'] + results['medium_risk_count'] + results['low_risk_count']}")
    
    print(f"\n2. Display Aggregation:")
    print(f"   - Total unique diseases: {results['total_diseases']}")
    print(f"   - Unique high-risk diseases: {results.get('unique_high_risk', 'N/A')}")
    print(f"   - Unique medium-risk diseases: {results.get('unique_medium_risk', 'N/A')}")
    print(f"   - Unique low-risk diseases: {results.get('unique_low_risk', 'N/A')}")
    
    print(f"\n3. Predictions List (Top 15):")
    top_preds = results['predictions'][:15]
    for idx, pred in enumerate(top_preds, 1):
        print(f"   {idx}. {pred['disease']:<20} - Risk: {pred['risk']:<6} - Confidence: {pred['confidence']}%")
    
    print(f"\n4. Validation:")
    if results['high_risk_count'] >= 15:
        print(f"   ✓ PASS: High-risk count ({results['high_risk_count']}) >= 15")
    else:
        print(f"   ✗ FAIL: High-risk count ({results['high_risk_count']}) < 15")
        print(f"   This is the reported bug!")
    
    # Save detailed results to file
    with open('test_15_patients_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n5. Detailed results saved to: test_15_patients_results.json")
    
    print(f"\n{'='*70}")
    
except Exception as e:
    logger.error(f"ERROR: {e}", exc_info=True)
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
