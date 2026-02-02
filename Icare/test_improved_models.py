#!/usr/bin/env python
"""
Test script for improved disease prediction models
Tests both rule-based and Hugging Face predictions
"""

from app.disease_predictor import predict_from_csv, DiseasePredictor

print("\n" + "="*60)
print("🏥 iCare Improved Disease Prediction System Test")
print("="*60)

# Test data - High risk patient
test_data = [{
    'age': '65',
    'gender': 'Male',
    'blood_pressure': '155/95',
    'cholesterol': '280',
    'glucose': '185'
}]

print("\n📋 Test Patient Data:")
print(f"  Age: 65 years")
print(f"  Gender: Male")
print(f"  Blood Pressure: 155/95 mmHg")
print(f"  Cholesterol: 280 mg/dL")
print(f"  Glucose: 185 mg/dL")

print("\n🔄 Running Prediction...")
results = predict_from_csv(test_data)

print("\n📊 Prediction Results Summary:")
print(f"  Total Diseases Analyzed: {results['total_diseases']}")
print(f"  Average Confidence: {results['avg_confidence']}%")
print(f"  Risk Breakdown:")
print(f"    - High Risk: {results['high_risk_count']} diseases")
print(f"    - Medium Risk: {results['medium_risk_count']} diseases")
print(f"    - Low Risk: {results['low_risk_count']} diseases")

print("\n🏆 Top 10 Disease Predictions:")
print("-" * 60)
for i, pred in enumerate(results['predictions'][:10], 1):
    model = pred.get("model", "unknown")
    risk_color = "🔴" if pred["risk"] == "High" else "🟠" if pred["risk"] == "Medium" else "🟢"
    print(f"{i:2d}. {pred['disease']:<20} {pred['confidence']:3d}% {risk_color} [{model}]")

print("\n" + "="*60)
print("✅ Test Completed Successfully!")
print("="*60 + "\n")
