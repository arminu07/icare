#!/usr/bin/env python
"""
Test to verify the format returned by predict_diseases for multiple patients
Run from: cd c:\Users\shahal Muhammed\OneDrive\Documents\GitHub\icare && python test_predict_format.py
"""
import os
import sys
import django

# Add Icare directory to path
icare_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Icare')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Icare.settings')
django.setup()

from app.disease_predictor import DiseasePredictor

# Create test data for 3 patients
test_medical_data = [
    {
        'age': '45',
        'gender': 'M',
        'blood_pressure': '140/90',
        'cholesterol': '250',
        'glucose': '130'
    },
    {
        'age': '55',
        'gender': 'F',
        'blood_pressure': '130/85',
        'cholesterol': '220',
        'glucose': '120'
    },
    {
        'age': '65',
        'gender': 'M',
        'blood_pressure': '150/95',
        'cholesterol': '280',
        'glucose': '150'
    }
]

print("="*70)
print("TEST: Check format of predict_diseases return value for multiple patients")
print("="*70)

try:
    predictor = DiseasePredictor()
    print(f"\n1. Calling predict_diseases with {len(test_medical_data)} patients...")
    predictions = predictor.predict_diseases(test_medical_data)
    
    print(f"\n2. Checking returned predictions:")
    print(f"   - Type of predictions: {type(predictions)}")
    print(f"   - Length of predictions: {len(predictions) if hasattr(predictions, '__len__') else 'N/A'}")
    
    if predictions:
        print(f"\n3. Checking first element:")
        print(f"   - Type of predictions[0]: {type(predictions[0])}")
        
        if isinstance(predictions[0], list):
            print(f"   ✓ predictions[0] is a list - CORRECT FORMAT for first patient")
            print(f"   - Length of predictions[0]: {len(predictions[0])}")
            if predictions[0]:
                print(f"   - Type of predictions[0][0]: {type(predictions[0][0])}")
                if isinstance(predictions[0][0], dict):
                    print(f"   - First disease: {predictions[0][0].get('disease')} ({predictions[0][0].get('risk')})")
        elif isinstance(predictions[0], dict):
            print(f"   ✗ ERROR: predictions[0] is a dict, not a list!")
            print(f"   - This means predictions is a FLAT list, not a list of lists")
            print(f"   - First disease: {predictions[0].get('disease')} ({predictions[0].get('risk')})")
    
    print(f"\n4. Summary:")
    if predictions and isinstance(predictions[0], list):
        print(f"   ✓ FORMAT IS CORRECT")
        print(f"   - predictions is a list of {len(predictions)} patient predictions")
        print(f"   - Each patient has ~{len(predictions[0])} disease predictions")
    elif predictions:
        print(f"   ✗ FORMAT IS WRONG")
        print(f"   - predictions appears to be a flat list of diseases, not multi-patient")
        print(f"   - Total predictions in flat list: {len(predictions)}")
    
    print("\n" + "="*70)
    
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()

