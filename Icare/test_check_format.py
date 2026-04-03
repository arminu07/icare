#!/usr/bin/env python
"""
Test to verify format returned by predict_diseases
Run from Icare directory: python test_check_format.py
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Icare.settings')
django.setup()

from app.disease_predictor import DiseasePredictor

test_medical_data = [
    {'age': '45', 'gender': 'M', 'blood_pressure': '140/90', 'cholesterol': '250', 'glucose': '130'},
    {'age': '55', 'gender': 'F', 'blood_pressure': '130/85', 'cholesterol': '220', 'glucose': '120'},
    {'age': '65', 'gender': 'M', 'blood_pressure': '150/95', 'cholesterol': '280', 'glucose': '150'}
]

print("="*70)
print("Check format from predict_diseases")
print("="*70)

predictor = DiseasePredictor()
predictions = predictor.predict_diseases(test_medical_data)

print(f"Type: {type(predictions)}")
print(f"Length: {len(predictions)}")

if predictions and isinstance(predictions[0], list):
    print(f"✓ Format CORRECT: List of lists [[pred1, pred2, ...], ...]")
    print(f"  - {len(predictions)} patient prediction lists")
    print(f"  - First patient has {len(predictions[0])} predictions")
elif predictions and isinstance(predictions[0], dict):
    print(f"✗ Format WRONG: Flat list [pred1, pred2, ...]")
    print(f"  - Total predictions: {len(predictions)}")
    print(f"  - This is a single flat list, not multi-patient format")
