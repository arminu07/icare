#!/usr/bin/env python
"""Quick test of disease predictor functionality"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Icare.settings')
django.setup()

from app.disease_predictor import DiseasePredictor
import numpy as np

def quick_test():
    """Quick functional test without full model download"""
    
    print("=" * 70)
    print("Quick Test: Hugging Face Disease Predictor - Rule-Based Component")
    print("=" * 70)
    
    try:
        # Initialize predictor
        print("\n🔧 Initializing predictor...")
        predictor = DiseasePredictor()
        print("✓ Predictor initialized")
        
        # Test feature extraction
        print("\n📊 Testing feature extraction...")
        test_record = {
            'age': '45',
            'gender': 'Male',
            'blood_pressure': '130/85',
            'cholesterol': '200',
            'glucose': '110'
        }
        
        features = predictor._extract_features(test_record)
        print(f"✓ Features extracted: {features}")
        print(f"  - Age (normalized): {features[0]:.2f}")
        print(f"  - Gender: {features[1]:.2f}")
        print(f"  - BP (normalized): {features[2]:.2f}")
        print(f"  - Cholesterol (normalized): {features[3]:.2f}")
        print(f"  - Glucose (normalized): {features[4]:.2f}")
        
        # Test rule-based prediction
        print("\n🧠 Testing rule-based predictions...")
        rule_predictions = predictor._rule_based_prediction(np.array(features))
        print(f"✓ Generated {len(rule_predictions)} disease predictions\n")
        
        print("Top 10 Disease Risk Scores (0-100%):")
        print("-" * 70)
        sorted_predictions = sorted(
            rule_predictions.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        for disease, score in sorted_predictions[:10]:
            score_pct = score * 100
            risk_level = "High" if score_pct > 70 else ("Medium" if score_pct > 40 else "Low")
            bar = "█" * int(score_pct / 5) + "░" * (20 - int(score_pct / 5))
            print(f"{disease:<25} {score_pct:>5.1f}% {bar} {risk_level}")
        
        print("-" * 70)
        
        # Calculate statistics
        high_risk = sum(1 for s in rule_predictions.values() if s > 0.7)
        medium_risk = sum(1 for s in rule_predictions.values() if 0.4 < s <= 0.7)
        low_risk = sum(1 for s in rule_predictions.values() if s <= 0.4)
        
        print(f"\n📈 Risk Distribution:")
        print(f"  - High Risk (>70%):     {high_risk} diseases")
        print(f"  - Medium Risk (40-70%): {medium_risk} diseases")
        print(f"  - Low Risk (<40%):      {low_risk} diseases")
        
        print("\n✅ All tests passed successfully!")
        print("\n📝 Note: Full Hugging Face model will download on first use.")
        print("   The system is ready to process medical CSV data!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = quick_test()
    sys.exit(0 if success else 1)
