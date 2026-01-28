"""
Disease Prediction using Rule-Based Approach
Fast rule-based disease prediction for instant response
"""

import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
import logging

logger = logging.getLogger(__name__)

class DiseasePredictor:
    """
    Predicts disease risk using rule-based heuristics
    Optimized for fast response in web applications
    """
    
    def __init__(self):
        """Initialize the disease prediction model"""
        self.classifier = None  # Optional lazy loading later
        
        # Disease categories
        self.disease_categories = [
            "Diabetes",
            "Heart Disease",
            "Hypertension",
            "Kidney Disease",
            "Thyroid Disorder",
            "Asthma",
            "Arthritis",
            "Cancer Risk",
            "Stroke Risk",
            "COPD",
            "Obesity",
            "Depression",
            "Anxiety",
            "Sleep Apnea",
            "Liver Disease"
        ]
        
        # Initialize scaler
        self.scaler = StandardScaler()
        self.fitted = False
        logger.info("✓ Disease Predictor initialized (rule-based mode)")
        
    def preprocess_medical_data(self, medical_data):
        """
        Preprocess medical data from CSV/form
        
        Args:
            medical_data: Dict or DataFrame with medical information
            
        Returns:
            Processed data ready for prediction
        """
        try:
            # Convert to DataFrame if dict
            if isinstance(medical_data, dict):
                medical_data = pd.DataFrame([medical_data])
            elif isinstance(medical_data, list):
                medical_data = pd.DataFrame(medical_data)
            
            # Clean column names
            medical_data.columns = [col.lower().strip() for col in medical_data.columns]
            
            # Create feature matrix
            features = []
            
            for idx, row in medical_data.iterrows():
                feature_vector = self._extract_features(row)
                features.append(feature_vector)
            
            features_array = np.array(features)
            
            # Fit and transform
            if not self.fitted:
                self.scaler.fit(features_array)
                self.fitted = True
            
            normalized_features = self.scaler.transform(features_array)
            
            return normalized_features, medical_data
            
        except Exception as e:
            logger.error(f"Error preprocessing medical data: {e}")
            raise
    
    def _extract_features(self, row):
        """Extract numerical features from medical record"""
        features = []
        
        # Age (normalized 0-100)
        try:
            age = float(row.get('age', 50))
            features.append(min(1.0, age / 100.0))
        except (ValueError, TypeError):
            features.append(0.5)
        
        # Gender (0=Female, 1=Male, 0.5=Other)
        try:
            gender = str(row.get('gender', 'M')).lower()
            gender_value = 1.0 if gender in ['m', 'male'] else (0.0 if gender in ['f', 'female'] else 0.5)
            features.append(gender_value)
        except:
            features.append(0.5)
        
        # Blood Pressure (systolic/diastolic -> average)
        try:
            bp = str(row.get('blood_pressure', '120/80'))
            systolic, diastolic = map(float, bp.replace(' ', '').split('/'))
            bp_avg = (systolic + diastolic) / 2 / 200.0
            features.append(min(1.0, bp_avg))
        except:
            features.append(0.6)
        
        # Cholesterol (normalized)
        try:
            cholesterol = float(row.get('cholesterol', 200))
            features.append(min(1.0, cholesterol / 300.0))
        except (ValueError, TypeError):
            features.append(0.5)
        
        # Glucose (normalized)
        try:
            glucose = float(row.get('glucose', 100))
            features.append(min(1.0, glucose / 200.0))
        except (ValueError, TypeError):
            features.append(0.5)
        
        return features
    
    def predict_diseases(self, medical_data):
        """
        Predict disease risks from medical data
        Uses fast rule-based approach
        
        Args:
            medical_data: Medical information (dict, list, or DataFrame)
            
        Returns:
            List of predictions with confidence scores
        """
        try:
            # Preprocess data
            features, original_data = self.preprocess_medical_data(medical_data)
            
            predictions_list = []
            
            for idx, feature_vector in enumerate(features):
                # Use fast rule-based prediction
                disease_probs = self._rule_based_prediction(feature_vector)
                predictions_list.append(disease_probs)
            
            return predictions_list
            
        except Exception as e:
            logger.error(f"Error in disease prediction: {e}")
            raise
    
    def _rule_based_prediction(self, feature_vector):
        """
        Fast rule-based disease prediction
        Returns predictions with confidence scores
        
        Args:
            feature_vector: Normalized features [age, gender, bp, cholesterol, glucose]
            
        Returns:
            Sorted list of disease predictions
        """
        age, gender, bp, cholesterol, glucose = feature_vector
        
        predictions = []
        
        # Diabetes risk (high glucose, age, cholesterol)
        diabetes_risk = min(1.0, glucose * 0.5 + age * 0.3 + cholesterol * 0.2)
        predictions.append({
            'disease': 'Diabetes',
            'confidence': max(5, int(diabetes_risk * 100)),
            'risk': 'High' if diabetes_risk > 0.7 else ('Medium' if diabetes_risk > 0.4 else 'Low')
        })
        
        # Heart Disease risk
        heart_risk = min(1.0, cholesterol * 0.4 + age * 0.4 + bp * 0.2)
        predictions.append({
            'disease': 'Heart Disease',
            'confidence': max(5, int(heart_risk * 100)),
            'risk': 'High' if heart_risk > 0.7 else ('Medium' if heart_risk > 0.4 else 'Low')
        })
        
        # Hypertension risk
        htn_risk = min(1.0, bp * 0.7 + age * 0.3)
        predictions.append({
            'disease': 'Hypertension',
            'confidence': max(5, int(htn_risk * 100)),
            'risk': 'High' if htn_risk > 0.7 else ('Medium' if htn_risk > 0.4 else 'Low')
        })
        
        # Kidney Disease risk
        kidney_risk = min(1.0, glucose * 0.4 + bp * 0.4 + age * 0.2)
        predictions.append({
            'disease': 'Kidney Disease',
            'confidence': max(5, int(kidney_risk * 100)),
            'risk': 'High' if kidney_risk > 0.7 else ('Medium' if kidney_risk > 0.4 else 'Low')
        })
        
        # Thyroid Disorder risk - use absolute value
        thyroid_risk = min(1.0, max(0, age * 0.3 + abs(cholesterol - 0.5) * 0.5))
        predictions.append({
            'disease': 'Thyroid Disorder',
            'confidence': max(5, int(thyroid_risk * 100)),
            'risk': 'High' if thyroid_risk > 0.7 else ('Medium' if thyroid_risk > 0.4 else 'Low')
        })
        
        # Asthma risk
        asthma_risk = min(1.0, age * 0.3 + max(0, 1 - age) * 0.3 + 0.4)
        predictions.append({
            'disease': 'Asthma',
            'confidence': max(5, int(asthma_risk * 100)),
            'risk': 'High' if asthma_risk > 0.7 else ('Medium' if asthma_risk > 0.4 else 'Low')
        })
        
        # Arthritis risk
        arthritis_risk = min(1.0, age * 0.8)
        predictions.append({
            'disease': 'Arthritis',
            'confidence': max(5, int(arthritis_risk * 100)),
            'risk': 'High' if arthritis_risk > 0.7 else ('Medium' if arthritis_risk > 0.4 else 'Low')
        })
        
        # Stroke Risk
        stroke_risk = min(1.0, cholesterol * 0.3 + bp * 0.4 + age * 0.3)
        predictions.append({
            'disease': 'Stroke Risk',
            'confidence': max(5, int(stroke_risk * 100)),
            'risk': 'High' if stroke_risk > 0.7 else ('Medium' if stroke_risk > 0.4 else 'Low')
        })
        
        # COPD risk
        copd_risk = min(1.0, age * 0.6 + 0.2)
        predictions.append({
            'disease': 'COPD',
            'confidence': max(5, int(copd_risk * 100)),
            'risk': 'High' if copd_risk > 0.7 else ('Medium' if copd_risk > 0.4 else 'Low')
        })
        
        # Obesity risk
        obesity_risk = min(1.0, glucose * 0.3 + cholesterol * 0.4 + 0.3)
        predictions.append({
            'disease': 'Obesity',
            'confidence': max(5, int(obesity_risk * 100)),
            'risk': 'High' if obesity_risk > 0.7 else ('Medium' if obesity_risk > 0.4 else 'Low')
        })
        
        # Depression risk
        depression_risk = min(1.0, max(0, 0.5 - age * 0.3) + 0.25)
        predictions.append({
            'disease': 'Depression',
            'confidence': max(5, int(depression_risk * 100)),
            'risk': 'High' if depression_risk > 0.7 else ('Medium' if depression_risk > 0.4 else 'Low')
        })
        
        # Anxiety risk
        anxiety_risk = min(1.0, max(0, 0.5 - age * 0.3) + 0.20)
        predictions.append({
            'disease': 'Anxiety',
            'confidence': max(5, int(anxiety_risk * 100)),
            'risk': 'High' if anxiety_risk > 0.7 else ('Medium' if anxiety_risk > 0.4 else 'Low')
        })
        
        # Sleep Apnea risk
        sleep_apnea_risk = min(1.0, max(0, obesity_risk * 0.4 + age * 0.4 + 0.2))
        predictions.append({
            'disease': 'Sleep Apnea',
            'confidence': max(5, int(sleep_apnea_risk * 100)),
            'risk': 'High' if sleep_apnea_risk > 0.7 else ('Medium' if sleep_apnea_risk > 0.4 else 'Low')
        })
        
        # Cancer Risk
        cancer_risk = min(1.0, age * 0.5 + cholesterol * 0.2 + 0.1)
        predictions.append({
            'disease': 'Cancer Risk',
            'confidence': max(5, int(cancer_risk * 100)),
            'risk': 'High' if cancer_risk > 0.7 else ('Medium' if cancer_risk > 0.4 else 'Low')
        })
        
        # Liver Disease
        liver_risk = min(1.0, glucose * 0.3 + cholesterol * 0.4 + 0.2)
        predictions.append({
            'disease': 'Liver Disease',
            'confidence': max(5, int(liver_risk * 100)),
            'risk': 'High' if liver_risk > 0.7 else ('Medium' if liver_risk > 0.4 else 'Low')
        })
        
        # Sort by confidence
        predictions = sorted(predictions, key=lambda x: x['confidence'], reverse=True)
        
        return predictions


def get_disease_predictor():
    """
    Get or create singleton instance of DiseasePredictor
    
    Returns:
        DiseasePredictor instance
    """
    if not hasattr(get_disease_predictor, '_instance'):
        get_disease_predictor._instance = DiseasePredictor()
    
    return get_disease_predictor._instance


def predict_from_csv(csv_data):
    """
    Predict diseases from CSV data
    
    Args:
        csv_data: List of dicts with medical information
        
    Returns:
        Predictions with statistics
    """
    try:
        predictor = get_disease_predictor()
        predictions = predictor.predict_diseases(csv_data)
        
        # Calculate statistics
        total_diseases = len(predictions[0]) if predictions else 0
        high_risk_count = sum(
            1 for p in predictions[0] 
            if p.get('risk') == 'High'
        ) if predictions else 0
        medium_risk_count = sum(
            1 for p in predictions[0] 
            if p.get('risk') == 'Medium'
        ) if predictions else 0
        low_risk_count = sum(
            1 for p in predictions[0] 
            if p.get('risk') == 'Low'
        ) if predictions else 0
        
        avg_confidence = (
            sum(p.get('confidence', 0) for p in predictions[0]) / len(predictions[0])
            if predictions and predictions[0]
            else 0
        )
        
        return {
            'predictions': predictions[0] if predictions else [],
            'total_diseases': total_diseases,
            'high_risk_count': high_risk_count,
            'medium_risk_count': medium_risk_count,
            'low_risk_count': low_risk_count,
            'avg_confidence': round(avg_confidence, 2)
        }
        
    except Exception as e:
        logger.error(f"Error in CSV prediction: {e}")
        raise
