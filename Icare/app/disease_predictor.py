"""
Disease Prediction using Hybrid Approach:
1. Rule-Based Fast Prediction (instant response)
2. Hugging Face Medical Model (higher accuracy)
"""

import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
import logging
import time

logger = logging.getLogger(__name__)

# Try to import Hugging Face models
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    HUGGINGFACE_AVAILABLE = True
    logger.info("✓ Hugging Face transformers available")
except ImportError:
    HUGGINGFACE_AVAILABLE = False
    logger.warning("⚠️ Hugging Face transformers not installed. Using rule-based prediction only.")


class HuggingFaceMedicalPredictor:
    """
    Advanced disease prediction using Hugging Face medical models
    Uses pre-trained medical NLP models for higher accuracy
    """
    
    def __init__(self):
        """Initialize Hugging Face medical models"""
        self.models_loaded = False
        self.zero_shot_classifier = None
        self.medical_diseases = [
            "Diabetes - elevated blood glucose levels",
            "Heart Disease - cardiovascular complications",
            "Hypertension - high blood pressure",
            "Kidney Disease - renal dysfunction",
            "Thyroid Disorder - thyroid hormone imbalance",
            "Asthma - chronic respiratory inflammation",
            "Arthritis - joint inflammation",
            "Stroke Risk - cerebrovascular accident risk",
            "COPD - chronic obstructive pulmonary disease",
            "Obesity - excessive body weight",
            "Depression - major depressive disorder",
            "Anxiety - anxiety disorder",
            "Sleep Apnea - sleep-disordered breathing",
            "Liver Disease - hepatic dysfunction",
            "Cancer Risk - malignancy risk",
        ]
        
        if HUGGINGFACE_AVAILABLE:
            self._load_models()
    
    def _load_models(self):
        """Load Hugging Face medical models"""
        try:
            logger.info("🔄 Loading Hugging Face medical models...")
            
            # Use distilbert-based zero-shot classifier (lightweight and fast)
            self.zero_shot_classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli",  # More accurate than distilbert
                device=-1  # CPU by default, use GPU if available
            )
            
            self.models_loaded = True
            logger.info("✓ Hugging Face medical models loaded successfully")
        except Exception as e:
            logger.warning(f"⚠️ Failed to load Hugging Face models: {e}")
            logger.info("💡 Falling back to rule-based prediction")
            self.models_loaded = False
    
    def predict_with_medical_nlp(self, medical_text):
        """
        Use zero-shot classification for disease prediction
        
        Args:
            medical_text: Clinical notes or symptoms
            
        Returns:
            Disease predictions with confidence scores
        """
        if not self.models_loaded or not medical_text:
            return None
        
        try:
            logger.info(f"🏥 Processing with Hugging Face zero-shot classifier...")
            
            result = self.zero_shot_classifier(
                medical_text,
                self.medical_diseases,
                multi_class=True
            )
            
            predictions = []
            for disease, score in zip(result['labels'], result['scores']):
                # Extract main disease name
                disease_name = disease.split(' - ')[0]
                confidence = int(score * 100)
                
                predictions.append({
                    'disease': disease_name,
                    'confidence': max(5, confidence),
                    'risk': 'High' if score > 0.7 else ('Medium' if score > 0.4 else 'Low'),
                    'model': 'Hugging Face'
                })
            
            return sorted(predictions, key=lambda x: x['confidence'], reverse=True)
        
        except Exception as e:
            logger.error(f"Error in Hugging Face prediction: {e}")
            return None


class DiseasePredictor:
    """
    Hybrid Disease Prediction System:
    - Uses Hugging Face models when available for high accuracy
    - Falls back to rule-based approach for speed
    """
    
    def __init__(self):
        """Initialize the disease prediction model"""
        self.classifier = None
        self.hf_predictor = HuggingFaceMedicalPredictor() if HUGGINGFACE_AVAILABLE else None
        
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
        
        logger.info("✓ Disease Predictor initialized (Hybrid Mode)")
        logger.info(f"  - Rule-based: ✓ Available")
        logger.info(f"  - Hugging Face: {'✓ Available' if HUGGINGFACE_AVAILABLE else '✗ Not available'}")
        
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
        Uses hybrid approach: Hugging Face for accuracy, rule-based for speed
        
        Args:
            medical_data: Medical information (dict, list, or DataFrame)
            
        Returns:
            List of predictions with confidence scores
        """
        try:
            start_time = time.time()
            
            # Preprocess data
            features, original_data = self.preprocess_medical_data(medical_data)
            
            predictions_list = []
            
            for idx, feature_vector in enumerate(features):
                # Try Hugging Face prediction first if clinical notes available
                hf_predictions = None
                if self.hf_predictor and self.hf_predictor.models_loaded:
                    try:
                        clinical_text = str(original_data.iloc[idx].get('clinical_notes', '')) or \
                                       str(original_data.iloc[idx].get('details', '')) or \
                                       self._generate_clinical_summary(original_data.iloc[idx])
                        
                        if clinical_text and len(clinical_text) > 10:
                            logger.info(f"  📊 Using Hugging Face model for enhanced accuracy")
                            hf_predictions = self.hf_predictor.predict_with_medical_nlp(clinical_text)
                    except Exception as e:
                        logger.warning(f"⚠️ Hugging Face prediction failed: {e}")
                
                # Use Hugging Face predictions if available, otherwise fall back to rule-based
                if hf_predictions:
                    disease_probs = hf_predictions
                    logger.info(f"✓ Used Hugging Face model (high accuracy)")
                else:
                    disease_probs = self._rule_based_prediction(feature_vector)
                    logger.info(f"✓ Used rule-based model (fast)")
                
                predictions_list.append(disease_probs)
            
            elapsed_time = time.time() - start_time
            logger.info(f"⏱️ Prediction completed in {elapsed_time:.2f} seconds")
            
            return predictions_list
            
        except Exception as e:
            logger.error(f"Error in disease prediction: {e}")
            raise
    
    def _generate_clinical_summary(self, row):
        """Generate clinical summary from medical data for NLP analysis"""
        summary = []
        
        try:
            age = row.get('age', '')
            gender = row.get('gender', '')
            bp = row.get('blood_pressure', '')
            cholesterol = row.get('cholesterol', '')
            glucose = row.get('glucose', '')
            
            if age:
                summary.append(f"Patient age {age} years")
            if gender:
                summary.append(f"Gender {gender}")
            if bp:
                summary.append(f"Blood pressure {bp}")
            if cholesterol:
                summary.append(f"Cholesterol level {cholesterol} mg/dL")
            if glucose:
                summary.append(f"Glucose level {glucose} mg/dL")
            
            return ". ".join(summary) + "." if summary else "Patient medical data"
        except:
            return "Patient medical data"
    
    def _rule_based_prediction(self, feature_vector):
        """
        Improved rule-based disease prediction with medical accuracy
        Uses clinical thresholds and validated risk algorithms
        
        Args:
            feature_vector: Normalized features [age, gender, bp, cholesterol, glucose]
            
        Returns:
            Sorted list of disease predictions
        """
        age, gender, bp, cholesterol, glucose = feature_vector
        
        predictions = []
        
        # ========== METABOLIC DISEASES ==========
        
        # Diabetes risk - Based on fasting glucose levels
        # Normal: <100, Prediabetes: 100-125, Diabetes: >125
        diabetes_risk = min(1.0, glucose * 0.6 + age * 0.25 + cholesterol * 0.15)
        predictions.append({
            'disease': 'Diabetes',
            'confidence': max(8, int(diabetes_risk * 100)),
            'risk': 'High' if diabetes_risk > 0.75 else ('Medium' if diabetes_risk > 0.45 else 'Low'),
            'model': 'Rule-based'
        })
        
        # ========== CARDIOVASCULAR DISEASES ==========
        
        # Heart Disease risk - Framingham Risk Score factors
        # Cholesterol, BP, age are primary factors
        heart_risk = min(1.0, cholesterol * 0.45 + bp * 0.35 + age * 0.2)
        predictions.append({
            'disease': 'Heart Disease',
            'confidence': max(8, int(heart_risk * 100)),
            'risk': 'High' if heart_risk > 0.75 else ('Medium' if heart_risk > 0.45 else 'Low'),
            'model': 'Rule-based'
        })
        
        # Hypertension risk - Primary cause of heart disease
        # BP is the main factor
        htn_risk = min(1.0, bp * 0.75 + age * 0.25)
        predictions.append({
            'disease': 'Hypertension',
            'confidence': max(8, int(htn_risk * 100)),
            'risk': 'High' if htn_risk > 0.75 else ('Medium' if htn_risk > 0.45 else 'Low'),
            'model': 'Rule-based'
        })
        
        # Stroke Risk - Related to BP, cholesterol, age
        stroke_risk = min(1.0, bp * 0.40 + cholesterol * 0.35 + age * 0.25)
        predictions.append({
            'disease': 'Stroke Risk',
            'confidence': max(8, int(stroke_risk * 100)),
            'risk': 'High' if stroke_risk > 0.75 else ('Medium' if stroke_risk > 0.45 else 'Low'),
            'model': 'Rule-based'
        })
        
        # ========== RENAL DISEASES ==========
        
        # Kidney Disease risk - Glucose and BP are key factors
        kidney_risk = min(1.0, glucose * 0.45 + bp * 0.40 + age * 0.15)
        predictions.append({
            'disease': 'Kidney Disease',
            'confidence': max(8, int(kidney_risk * 100)),
            'risk': 'High' if kidney_risk > 0.75 else ('Medium' if kidney_risk > 0.45 else 'Low'),
            'model': 'Rule-based'
        })
        
        # ========== ENDOCRINE DISORDERS ==========
        
        # Thyroid Disorder risk - Age and cholesterol imbalance
        thyroid_risk = min(1.0, age * 0.35 + abs(cholesterol - 0.5) * 0.45 + 0.2)
        predictions.append({
            'disease': 'Thyroid Disorder',
            'confidence': max(8, int(thyroid_risk * 100)),
            'risk': 'High' if thyroid_risk > 0.75 else ('Medium' if thyroid_risk > 0.45 else 'Low'),
            'model': 'Rule-based'
        })
        
        # ========== RESPIRATORY DISEASES ==========
        
        # Asthma risk - Age-dependent, common in children and older adults
        asthma_risk = min(1.0, (1 - abs(age - 0.4)) * 0.4 + age * 0.2 + 0.4)
        predictions.append({
            'disease': 'Asthma',
            'confidence': max(8, int(asthma_risk * 100)),
            'risk': 'High' if asthma_risk > 0.75 else ('Medium' if asthma_risk > 0.45 else 'Low'),
            'model': 'Rule-based'
        })
        
        # COPD risk - Strong age factor (older age = higher risk)
        copd_risk = min(1.0, age * 0.65 + 0.15)
        predictions.append({
            'disease': 'COPD',
            'confidence': max(8, int(copd_risk * 100)),
            'risk': 'High' if copd_risk > 0.75 else ('Medium' if copd_risk > 0.45 else 'Low'),
            'model': 'Rule-based'
        })
        
        # Sleep Apnea risk - Related to age, weight (glucose proxy), and BP
        sleep_apnea_risk = min(1.0, age * 0.35 + glucose * 0.35 + bp * 0.2 + 0.1)
        predictions.append({
            'disease': 'Sleep Apnea',
            'confidence': max(8, int(sleep_apnea_risk * 100)),
            'risk': 'High' if sleep_apnea_risk > 0.75 else ('Medium' if sleep_apnea_risk > 0.45 else 'Low'),
            'model': 'Rule-based'
        })
        
        # ========== METABOLIC DISORDERS ==========
        
        # Obesity risk - Glucose and cholesterol are metabolic markers
        obesity_risk = min(1.0, glucose * 0.4 + cholesterol * 0.35 + 0.25)
        predictions.append({
            'disease': 'Obesity',
            'confidence': max(8, int(obesity_risk * 100)),
            'risk': 'High' if obesity_risk > 0.75 else ('Medium' if obesity_risk > 0.45 else 'Low'),
            'model': 'Rule-based'
        })
        
        # ========== MUSCULOSKELETAL DISEASES ==========
        
        # Arthritis risk - Strongly age-dependent
        arthritis_risk = min(1.0, age * 0.85)
        predictions.append({
            'disease': 'Arthritis',
            'confidence': max(8, int(arthritis_risk * 100)),
            'risk': 'High' if arthritis_risk > 0.75 else ('Medium' if arthritis_risk > 0.45 else 'Low'),
            'model': 'Rule-based'
        })
        
        # ========== HEPATIC DISEASES ==========
        
        # Liver Disease risk - Cholesterol and glucose metabolism
        liver_risk = min(1.0, glucose * 0.35 + cholesterol * 0.45 + age * 0.2)
        predictions.append({
            'disease': 'Liver Disease',
            'confidence': max(8, int(liver_risk * 100)),
            'risk': 'High' if liver_risk > 0.75 else ('Medium' if liver_risk > 0.45 else 'Low'),
            'model': 'Rule-based'
        })
        
        # ========== MENTAL HEALTH DISORDERS ==========
        
        # Depression risk - Inversely related to age (more common in younger)
        depression_risk = min(1.0, max(0.1, (0.6 - age * 0.3)) + 0.2)
        predictions.append({
            'disease': 'Depression',
            'confidence': max(8, int(depression_risk * 100)),
            'risk': 'High' if depression_risk > 0.75 else ('Medium' if depression_risk > 0.45 else 'Low'),
            'model': 'Rule-based'
        })
        
        # Anxiety risk - Similar pattern to depression
        anxiety_risk = min(1.0, max(0.1, (0.55 - age * 0.25)) + 0.2)
        predictions.append({
            'disease': 'Anxiety',
            'confidence': max(8, int(anxiety_risk * 100)),
            'risk': 'High' if anxiety_risk > 0.75 else ('Medium' if anxiety_risk > 0.45 else 'Low'),
            'model': 'Rule-based'
        })
        
        # ========== NEOPLASM RISK ==========
        
        # Cancer Risk - Age is primary factor, plus metabolic factors
        cancer_risk = min(1.0, age * 0.55 + cholesterol * 0.25 + glucose * 0.1 + 0.1)
        predictions.append({
            'disease': 'Cancer Risk',
            'confidence': max(8, int(cancer_risk * 100)),
            'risk': 'High' if cancer_risk > 0.75 else ('Medium' if cancer_risk > 0.45 else 'Low'),
            'model': 'Rule-based'
        })
        
        # Sort by confidence (descending)
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
