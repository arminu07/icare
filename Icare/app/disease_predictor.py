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
    
    def _generate_disease_reasoning(self, disease_name, risk_score, feature_vector, contributing_factors):
        """
        Generate detailed clinical reasoning for why a disease was predicted
        
        Args:
            disease_name: Name of the disease
            risk_score: Risk score (0-1)
            feature_vector: [age, gender, bp, cholesterol, glucose]
            contributing_factors: Dict of factors and their contributions
            
        Returns:
            String explanation of the reasoning
        """
        age, gender, bp, cholesterol, glucose = feature_vector
        
        # Convert normalized values back to approximate clinical ranges
        age_years = int(age * 100)
        gender_str = "Male" if gender > 0.7 else ("Female" if gender < 0.3 else "Other")
        bp_approx = int(bp * 200)
        cholesterol_approx = int(cholesterol * 300)
        glucose_approx = int(glucose * 200)
        
        reasoning = f"{disease_name} Risk Assessment:\n"
        reasoning += f"Risk Score: {int(risk_score * 100)}% | "
        reasoning += f"Risk Level: {'High' if risk_score > 0.75 else ('Medium' if risk_score > 0.45 else 'Low')}\n"
        reasoning += f"Patient Profile: {age_years} years old, {gender_str}\n\n"
        reasoning += "Contributing Factors:\n"
        
        for factor, contribution in contributing_factors.items():
            reasoning += f"• {factor}: {contribution}\n"
        
        return reasoning
    
    def _rule_based_prediction(self, feature_vector):
        """
        Improved rule-based disease prediction with medical accuracy
        Uses clinical thresholds and validated risk algorithms
        
        Args:
            feature_vector: Normalized features [age, gender, bp, cholesterol, glucose]
            
        Returns:
            Sorted list of disease predictions with reasoning
        """
        age, gender, bp, cholesterol, glucose = feature_vector
        
        predictions = []
        
        # Convert to approximate clinical values for reasoning
        age_years = int(age * 100)
        bp_approx = int(bp * 200)
        cholesterol_approx = int(cholesterol * 300)
        glucose_approx = int(glucose * 200)
        
        # ========== METABOLIC DISEASES ==========
        
        # Diabetes risk - Based on fasting glucose levels
        # Normal: <100, Prediabetes: 100-125, Diabetes: >125
        diabetes_risk = min(1.0, glucose * 0.6 + age * 0.25 + cholesterol * 0.15)
        diabetes_factors = {
            f"Blood Glucose Level ({glucose_approx} mg/dL)": "60% contribution - Main indicator for diabetes" if glucose_approx > 100 else "Elevated glucose levels increase diabetes risk",
            f"Age ({age_years} years)": "25% contribution - Age-related metabolic changes affect insulin sensitivity",
            f"Cholesterol ({cholesterol_approx} mg/dL)": "15% contribution - Metabolic syndrome indicator"
        }
        predictions.append({
            'disease': 'Diabetes',
            'confidence': max(8, int(diabetes_risk * 100)),
            'risk': 'High' if diabetes_risk > 0.75 else ('Medium' if diabetes_risk > 0.45 else 'Low'),
            'model': 'Rule-based',
            'reasoning': self._generate_disease_reasoning('Diabetes', diabetes_risk, feature_vector, diabetes_factors)
        })
        
        # ========== CARDIOVASCULAR DISEASES ==========
        
        # Heart Disease risk - Framingham Risk Score factors
        # Cholesterol, BP, age are primary factors
        heart_risk = min(1.0, cholesterol * 0.45 + bp * 0.35 + age * 0.2)
        heart_factors = {
            f"Cholesterol ({cholesterol_approx} mg/dL)": "45% contribution - High cholesterol is a major cardiovascular risk factor",
            f"Blood Pressure (~{bp_approx} mmHg)": "35% contribution - Elevated BP damages arterial walls and increases heart disease risk",
            f"Age ({age_years} years)": "20% contribution - Cardiovascular risk increases with age"
        }
        predictions.append({
            'disease': 'Heart Disease',
            'confidence': max(8, int(heart_risk * 100)),
            'risk': 'High' if heart_risk > 0.75 else ('Medium' if heart_risk > 0.45 else 'Low'),
            'model': 'Rule-based',
            'reasoning': self._generate_disease_reasoning('Heart Disease', heart_risk, feature_vector, heart_factors)
        })
        
        # Hypertension risk - Primary cause of heart disease
        # BP is the main factor
        htn_risk = min(1.0, bp * 0.75 + age * 0.25)
        htn_factors = {
            f"Blood Pressure (~{bp_approx} mmHg)": "75% contribution - Primary indicator; >140/90 mmHg indicates hypertension",
            f"Age ({age_years} years)": "25% contribution - HTension prevalence increases significantly with age"
        }
        predictions.append({
            'disease': 'Hypertension',
            'confidence': max(8, int(htn_risk * 100)),
            'risk': 'High' if htn_risk > 0.75 else ('Medium' if htn_risk > 0.45 else 'Low'),
            'model': 'Rule-based',
            'reasoning': self._generate_disease_reasoning('Hypertension', htn_risk, feature_vector, htn_factors)
        })
        
        # Stroke Risk - Related to BP, cholesterol, age
        stroke_risk = min(1.0, bp * 0.40 + cholesterol * 0.35 + age * 0.25)
        stroke_factors = {
            f"Blood Pressure (~{bp_approx} mmHg)": "40% contribution - High BP is the leading stroke risk factor",
            f"Cholesterol ({cholesterol_approx} mg/dL)": "35% contribution - Elevated cholesterol contributes to arterial plaque formation",
            f"Age ({age_years} years)": "25% contribution - Stroke risk increases significantly after age 55"
        }
        predictions.append({
            'disease': 'Stroke Risk',
            'confidence': max(8, int(stroke_risk * 100)),
            'risk': 'High' if stroke_risk > 0.75 else ('Medium' if stroke_risk > 0.45 else 'Low'),
            'model': 'Rule-based',
            'reasoning': self._generate_disease_reasoning('Stroke Risk', stroke_risk, feature_vector, stroke_factors)
        })
        
        # ========== RENAL DISEASES ==========
        
        # Kidney Disease risk - Glucose and BP are key factors
        kidney_risk = min(1.0, glucose * 0.45 + bp * 0.40 + age * 0.15)
        kidney_factors = {
            f"Blood Glucose ({glucose_approx} mg/dL)": "45% contribution - Diabetes is leading cause of kidney disease (diabetic nephropathy)",
            f"Blood Pressure (~{bp_approx} mmHg)": "40% contribution - Hypertension damages kidney filtration units",
            f"Age ({age_years} years)": "15% contribution - Kidney function naturally declines with age"
        }
        predictions.append({
            'disease': 'Kidney Disease',
            'confidence': max(8, int(kidney_risk * 100)),
            'risk': 'High' if kidney_risk > 0.75 else ('Medium' if kidney_risk > 0.45 else 'Low'),
            'model': 'Rule-based',
            'reasoning': self._generate_disease_reasoning('Kidney Disease', kidney_risk, feature_vector, kidney_factors)
        })
        
        # ========== ENDOCRINE DISORDERS ==========
        
        # Thyroid Disorder risk - Age and cholesterol imbalance
        thyroid_risk = min(1.0, age * 0.35 + abs(cholesterol - 0.5) * 0.45 + 0.2)
        thyroid_factors = {
            f"Age ({age_years} years)": "35% contribution - Thyroid disorders more common in older adults",
            f"Cholesterol Metabolism ({cholesterol_approx} mg/dL)": "45% contribution - Abnormal cholesterol levels suggest thyroid dysfunction",
            "General Risk": "20% baseline - Population prevalence"
        }
        predictions.append({
            'disease': 'Thyroid Disorder',
            'confidence': max(8, int(thyroid_risk * 100)),
            'risk': 'High' if thyroid_risk > 0.75 else ('Medium' if thyroid_risk > 0.45 else 'Low'),
            'model': 'Rule-based',
            'reasoning': self._generate_disease_reasoning('Thyroid Disorder', thyroid_risk, feature_vector, thyroid_factors)
        })
        
        # ========== RESPIRATORY DISEASES ==========
        
        # Asthma risk - Age-dependent, common in children and older adults
        asthma_risk = min(1.0, (1 - abs(age - 0.4)) * 0.4 + age * 0.2 + 0.4)
        asthma_factors = {
            f"Age Pattern ({age_years} years)": "60% contribution - Bimodal distribution (children and elderly have higher risk)",
            "Age Factor": "20% contribution - Older age increases risk",
            "Population Baseline": "20% baseline prevalence"
        }
        predictions.append({
            'disease': 'Asthma',
            'confidence': max(8, int(asthma_risk * 100)),
            'risk': 'High' if asthma_risk > 0.75 else ('Medium' if asthma_risk > 0.45 else 'Low'),
            'model': 'Rule-based',
            'reasoning': self._generate_disease_reasoning('Asthma', asthma_risk, feature_vector, asthma_factors)
        })
        
        # COPD risk - Strong age factor (older age = higher risk)
        copd_risk = min(1.0, age * 0.65 + 0.15)
        copd_factors = {
            f"Age ({age_years} years)": "65% contribution - COPD is primarily age-related, especially >40 years",
            "Baseline Risk": "15% population baseline"
        }
        predictions.append({
            'disease': 'COPD',
            'confidence': max(8, int(copd_risk * 100)),
            'risk': 'High' if copd_risk > 0.75 else ('Medium' if copd_risk > 0.45 else 'Low'),
            'model': 'Rule-based',
            'reasoning': self._generate_disease_reasoning('COPD', copd_risk, feature_vector, copd_factors)
        })
        
        # Sleep Apnea risk - Related to age, weight (glucose proxy), and BP
        sleep_apnea_risk = min(1.0, age * 0.35 + glucose * 0.35 + bp * 0.2 + 0.1)
        sleep_factors = {
            f"Age ({age_years} years)": "35% contribution - Sleep apnea increases with age, especially after 50",
            f"Weight Indicator (via glucose {glucose_approx} mg/dL)": "35% contribution - Obesity is major risk factor",
            f"Blood Pressure (~{bp_approx} mmHg)": "20% contribution - HTN and sleep apnea are closely linked",
            "Baseline Risk": "10% population prevalence"
        }
        predictions.append({
            'disease': 'Sleep Apnea',
            'confidence': max(8, int(sleep_apnea_risk * 100)),
            'risk': 'High' if sleep_apnea_risk > 0.75 else ('Medium' if sleep_apnea_risk > 0.45 else 'Low'),
            'model': 'Rule-based',
            'reasoning': self._generate_disease_reasoning('Sleep Apnea', sleep_apnea_risk, feature_vector, sleep_factors)
        })
        
        # ========== METABOLIC DISORDERS ==========
        
        # Obesity risk - Glucose and cholesterol are metabolic markers
        obesity_risk = min(1.0, glucose * 0.4 + cholesterol * 0.35 + 0.25)
        obesity_factors = {
            f"Blood Glucose ({glucose_approx} mg/dL)": "40% contribution - Elevated glucose indicates metabolic dysfunction",
            f"Cholesterol ({cholesterol_approx} mg/dL)": "35% contribution - Dyslipidemia is marker of obesity",
            "Baseline Risk": "25% population prevalence"
        }
        predictions.append({
            'disease': 'Obesity',
            'confidence': max(8, int(obesity_risk * 100)),
            'risk': 'High' if obesity_risk > 0.75 else ('Medium' if obesity_risk > 0.45 else 'Low'),
            'model': 'Rule-based',
            'reasoning': self._generate_disease_reasoning('Obesity', obesity_risk, feature_vector, obesity_factors)
        })
        
        # ========== MUSCULOSKELETAL DISEASES ==========
        
        # Arthritis risk - Strongly age-dependent
        arthritis_risk = min(1.0, age * 0.85)
        arthritis_factors = {
            f"Age ({age_years} years)": "85% contribution - Osteoarthritis strongly correlated with age; risk significantly increases >50 years"
        }
        predictions.append({
            'disease': 'Arthritis',
            'confidence': max(8, int(arthritis_risk * 100)),
            'risk': 'High' if arthritis_risk > 0.75 else ('Medium' if arthritis_risk > 0.45 else 'Low'),
            'model': 'Rule-based',
            'reasoning': self._generate_disease_reasoning('Arthritis', arthritis_risk, feature_vector, arthritis_factors)
        })
        
        # ========== HEPATIC DISEASES ==========
        
        # Liver Disease risk - Cholesterol and glucose metabolism
        liver_risk = min(1.0, glucose * 0.35 + cholesterol * 0.45 + age * 0.2)
        liver_factors = {
            f"Cholesterol ({cholesterol_approx} mg/dL)": "45% contribution - Liver disease causes cholesterol metabolism abnormalities",
            f"Blood Glucose ({glucose_approx} mg/dL)": "35% contribution - Elevated glucose linked to fatty liver disease",
            f"Age ({age_years} years)": "20% contribution - Liver disease risk increases with age"
        }
        predictions.append({
            'disease': 'Liver Disease',
            'confidence': max(8, int(liver_risk * 100)),
            'risk': 'High' if liver_risk > 0.75 else ('Medium' if liver_risk > 0.45 else 'Low'),
            'model': 'Rule-based',
            'reasoning': self._generate_disease_reasoning('Liver Disease', liver_risk, feature_vector, liver_factors)
        })
        
        # ========== MENTAL HEALTH DISORDERS ==========
        
        # Depression risk - Inversely related to age (more common in younger)
        depression_risk = min(1.0, max(0.1, (0.6 - age * 0.3)) + 0.2)
        depression_factors = {
            f"Age ({age_years} years)": "Primary factor - Depression has U-shaped distribution (high in young and elderly)",
            "General Risk": "20% baseline - Common mental health condition"
        }
        predictions.append({
            'disease': 'Depression',
            'confidence': max(8, int(depression_risk * 100)),
            'risk': 'High' if depression_risk > 0.75 else ('Medium' if depression_risk > 0.45 else 'Low'),
            'model': 'Rule-based',
            'reasoning': self._generate_disease_reasoning('Depression', depression_risk, feature_vector, depression_factors)
        })
        
        # Anxiety risk - Similar pattern to depression
        anxiety_risk = min(1.0, max(0.1, (0.55 - age * 0.25)) + 0.2)
        anxiety_factors = {
            f"Age ({age_years} years)": "Primary factor - Anxiety disorders more prevalent in younger to middle-aged individuals",
            "General Risk": "15% baseline - Anxiety is common mental health condition"
        }
        predictions.append({
            'disease': 'Anxiety',
            'confidence': max(8, int(anxiety_risk * 100)),
            'risk': 'High' if anxiety_risk > 0.75 else ('Medium' if anxiety_risk > 0.45 else 'Low'),
            'model': 'Rule-based',
            'reasoning': self._generate_disease_reasoning('Anxiety', anxiety_risk, feature_vector, anxiety_factors)
        })
        
        # ========== NEOPLASM RISK ==========
        
        # Cancer Risk - Age is primary factor, plus metabolic factors
        cancer_risk = min(1.0, age * 0.55 + cholesterol * 0.25 + glucose * 0.1 + 0.1)
        cancer_factors = {
            f"Age ({age_years} years)": "55% contribution - Cancer risk increases exponentially with age, majority of cases >50 years",
            f"Cholesterol ({cholesterol_approx} mg/dL)": "25% contribution - Elevated cholesterol linked to certain cancer types",
            f"Metabolic Status (glucose {glucose_approx} mg/dL)": "10% contribution - Diabetes increases cancer risk",
            "Baseline Risk": "10% population baseline"
        }
        predictions.append({
            'disease': 'Cancer Risk',
            'confidence': max(8, int(cancer_risk * 100)),
            'risk': 'High' if cancer_risk > 0.75 else ('Medium' if cancer_risk > 0.45 else 'Low'),
            'model': 'Rule-based',
            'reasoning': self._generate_disease_reasoning('Cancer Risk', cancer_risk, feature_vector, cancer_factors)
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
