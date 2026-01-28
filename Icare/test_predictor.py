#!/usr/bin/env python
"""Test script for Hugging Face disease predictor"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Icare.settings')
django.setup()

from app.disease_predictor import predict_from_csv

def test_predictor():
    """Test the disease predictor with sample data"""
    
    print("=" * 60)
    print("Testing Hugging Face Disease Predictor")
    print("=" * 60)
    
    # Test data
    medical_data = [
        {
            'age': '45',
            'gender': 'Male',
            'blood_pressure': '130/85',
            'cholesterol': '200',
            'glucose': '110',
            'disease_type': 'Test'
        },
        {
            'age': '65',
            'gender': 'Female',
            'blood_pressure': '160/100',
            'cholesterol': '280',
            'glucose': '140',
            'disease_type': 'Test2'
        }
    ]
    
    print("\n📊 Input Data:")
    for i, record in enumerate(medical_data, 1):
        print(f"  Patient {i}:")
        print(f"    - Age: {record['age']}")
        print(f"    - Gender: {record['gender']}")
        print(f"    - BP: {record['blood_pressure']}")
        print(f"    - Cholesterol: {record['cholesterol']}")
        print(f"    - Glucose: {record['glucose']}")
    
    print("\n🧠 Running Hugging Face ML Prediction...")
    
    try:
        results = predict_from_csv(medical_data)
        
        print("✅ Prediction Successful!\n")
        print(f"📈 Results Summary:")
        print(f"  - Total Diseases Analyzed: {results['total_diseases']}")
        print(f"  - High Risk Count: {results['high_risk_count']}")
        print(f"  - Medium Risk Count: {results['medium_risk_count']}")
        print(f"  - Low Risk Count: {results['low_risk_count']}")
        print(f"  - Average Confidence: {results['avg_confidence']}%\n")
        
        print("🏥 Top 10 Disease Predictions:")
        print("-" * 60)
        print(f"{'Disease':<25} {'Confidence':<12} {'Risk Level':<12}")
        print("-" * 60)
        
        for pred in results['predictions'][:10]:
            disease = pred['disease']
            confidence = pred['confidence']
            risk = pred['risk']
            
            # Color code the risk
            if risk == 'High':
                risk_display = f"🔴 {risk}"
            elif risk == 'Medium':
                risk_display = f"🟡 {risk}"
            else:
                risk_display = f"🟢 {risk}"
            
            print(f"{disease:<25} {confidence:>8}%     {risk_display:<12}")
        
        print("-" * 60)
        print("\n✓ Test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_predictor()
    sys.exit(0 if success else 1)
