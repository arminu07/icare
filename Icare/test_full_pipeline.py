#!/usr/bin/env python
"""
Quick test of the disease predictor with CSV data
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Icare.settings')
django.setup()

from app.disease_predictor import predict_from_csv
import csv

# Read test CSV
print("=" * 60)
print("Testing Disease Predictor with CSV Data")
print("=" * 60)

with open('test_sample.csv', 'r') as f:
    decoded_file = f.read().splitlines()

csv_reader = csv.DictReader(decoded_file)
medical_data = list(csv_reader)

print(f"\n✓ Loaded {len(medical_data)} records from test_sample.csv")
print(f"✓ Headers: {list(medical_data[0].keys())}")
print(f"✓ First record: {medical_data[0]}\n")

try:
    print("Running disease prediction...")
    results = predict_from_csv(medical_data)
    
    print(f"\n✓ PREDICTION SUCCESSFUL!")
    print(f"  - Total Diseases Analyzed: {results['total_diseases']}")
    print(f"  - High Risk Count: {results['high_risk_count']}")
    print(f"  - Medium Risk Count: {results['medium_risk_count']}")
    print(f"  - Low Risk Count: {results['low_risk_count']}")
    print(f"  - Average Confidence: {results['avg_confidence']}%")
    
    print(f"\n✓ Top 5 Predictions:")
    for i, pred in enumerate(results['predictions'][:5], 1):
        print(f"  {i}. {pred['disease']}: {pred['confidence']}% ({pred['risk']})")
    
    print("\n" + "=" * 60)
    print("✓ ALL TESTS PASSED")
    print("=" * 60)
    
except Exception as e:
    print(f"\n✗ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
