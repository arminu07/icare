"""
Disease Precautions and Health Recommendations
Provides prevention tips, dietary advice, and warning signs for various diseases.
"""

import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


# Dictionary mapping diseases to their precautions and health recommendations
DISEASE_PRECAUTIONS = {
    "Diabetes": {
        "icon": "🩺",
        "precautions": [
            "Check blood glucose levels regularly as recommended by your doctor",
            "Follow a consistent meal plan with balanced carbohydrates and fiber",
            "Exercise regularly for at least 150 minutes per week",
            "Maintain a healthy body weight through balanced diet and exercise",
            "Manage stress through meditation, yoga, or other relaxation techniques",
            "Take medications exactly as prescribed by your healthcare provider"
        ],
        "diet_tips": "Focus on whole grains, lean proteins, healthy fats, and plenty of vegetables. Limit sugars, refined carbohydrates, and processed foods. Stay hydrated with water instead of sugary beverages.",
        "when_to_see_doctor": "Seek immediate medical attention if you experience extreme thirst, blurred vision, numbness in extremities, persistent fatigue, or frequent infections. Also see your doctor if blood glucose readings are consistently high or low."
    },
    "Heart Disease": {
        "icon": "❤️",
        "precautions": [
            "Maintain a low-sodium diet rich in heart-healthy fats",
            "Exercise regularly - aim for 150 minutes of aerobic activity weekly",
            "Manage stress through relaxation techniques like deep breathing",
            "Avoid smoking and secondhand smoke exposure",
            "Monitor blood pressure and cholesterol regularly",
            "Take prescribed cardiovascular medications consistently"
        ],
        "diet_tips": "Consume heart-healthy fats from olive oil, nuts, and fatty fish rich in omega-3 fatty acids. Eat plenty of vegetables, fruits, whole grains, and lean proteins. Limit saturated fats, trans fats, and sodium.",
        "when_to_see_doctor": "Seek emergency care if you experience chest pain, shortness of breath, severe heart palpitations, or fainting. Schedule regular check-ups and inform your doctor of any unusual symptoms or lifestyle changes."
    },
    "Hypertension": {
        "icon": "🩸",
        "precautions": [
            "Monitor blood pressure at home regularly and keep a log",
            "Reduce sodium intake to less than 2,300mg per day",
            "Maintain a regular exercise routine of at least 30 minutes daily",
            "Practice stress reduction techniques like meditation or yoga",
            "Maintain a healthy weight through proper diet and exercise",
            "Limit caffeine and alcohol consumption"
        ],
        "diet_tips": "Follow a DASH diet rich in fruits, vegetables, whole grains, lean proteins, and low-fat dairy. Reduce salt intake by avoiding processed foods and using herbs for flavoring instead of salt.",
        "when_to_see_doctor": "Seek emergency care if you have severe headaches, chest pain, shortness of breath, or blurred vision. Report any consistent readings above 180/120 to your doctor immediately."
    },
    "Stroke": {
        "icon": "🧠",
        "precautions": [
            "Control high blood pressure through medication and lifestyle changes",
            "Manage blood sugar levels if diabetic through proper diet and exercise",
            "Avoid smoking and secondhand smoke as they increase stroke risk",
            "Exercise regularly to maintain cardiovascular health",
            "Maintain a healthy weight and balanced diet",
            "Take antiplatelet medications as prescribed by your doctor"
        ],
        "diet_tips": "Eat foods rich in potassium like bananas and sweet potatoes. Consume fatty fish high in omega-3s at least twice weekly. Avoid high-salt and high-fat processed foods that increase stroke risk.",
        "when_to_see_doctor": "Seek immediate emergency care if you experience sudden weakness on one side, facial drooping, speech difficulties, or severe headache. These may be signs of stroke - call emergency services immediately."
    },
    "Kidney Disease": {
        "icon": "🫘",
        "precautions": [
            "Control blood pressure and blood sugar levels consistently",
            "Take kidney-protective medications as prescribed",
            "Stay hydrated but avoid excessive fluid intake if advised",
            "Get regular kidney function tests and monitor results",
            "Maintain a healthy weight through balanced nutrition",
            "Avoid NSAIDs and other medications harmful to kidneys"
        ],
        "diet_tips": "Limit protein intake and choose high-quality proteins like lean fish. Reduce sodium to less than 2,000mg daily. Limit potassium and phosphorus intake as recommended by your nephrologist. Stay well-hydrated.",
        "when_to_see_doctor": "Report any changes in urination patterns, blood in urine, swelling of hands/feet, or persistent fatigue. Schedule regular monitoring appointments and follow all treatment recommendations."
    },
    "Liver Disease": {
        "icon": "🏥",
        "precautions": [
            "Avoid alcohol completely if you have liver disease",
            "Limit fat intake and maintain a balanced, healthy diet",
            "Get vaccinated for hepatitis A and B if not immune",
            "Avoid sharing personal items that could transmit hepatitis",
            "Take prescribed medications for liver conditions regularly",
            "Avoid over-the-counter medications and supplements that stress the liver"
        ],
        "diet_tips": "Eat a balanced diet with adequate protein, whole grains, fruits, and vegetables. Avoid fatty, fried, and processed foods. Limit salt intake and maintain proper hydration. Consult a dietitian for personalized guidance.",
        "when_to_see_doctor": "Seek medical care if you notice yellowing of skin/eyes, abdominal swelling, dark urine, pale stools, or persistent nausea. Schedule regular liver function tests and specialist visits as recommended."
    },
    "Anemia": {
        "icon": "🩸",
        "precautions": [
            "Eat iron-rich foods regularly or take iron supplements as prescribed",
            "Improve iron absorption by pairing iron foods with vitamin C sources",
            "Get adequate B12 and folate through diet or supplements",
            "Avoid substances that inhibit iron absorption like caffeine with meals",
            "Take ferrous supplements with water on an empty stomach if possible",
            "Have regular blood tests to monitor hemoglobin levels"
        ],
        "diet_tips": "Consume iron-rich foods like lean red meat, poultry, fish, beans, lentils, and fortified cereals. Include citrus fruits, berries, and tomatoes to enhance iron absorption. Eat B12-rich foods or consider supplementation.",
        "when_to_see_doctor": "Report severe fatigue, persistent shortness of breath, chest pain, or unusual bleeding. Get regular blood counts and adjust treatment as needed based on test results."
    },
    "Asthma": {
        "icon": "💨",
        "precautions": [
            "Use prescribed inhalers correctly and consistently as directed",
            "Identify and avoid personal asthma triggers",
            "Keep emergency rescue inhaler with you at all times",
            "Monitor peak flow measurements regularly at home",
            "Avoid respiratory infections through handwashing and vaccination",
            "Maintain an asthma action plan and share it with caregivers"
        ],
        "diet_tips": "Eat antioxidant-rich foods like berries, citrus fruits, and leafy greens. Include omega-3 foods like fatty fish. Avoid food triggers if identified. Stay well-hydrated with water and warm beverages.",
        "when_to_see_doctor": "Seek emergency care for severe shortness of breath, chest tightness, or if rescue inhaler doesn't work. Schedule regular check-ups to adjust medications based on symptom control and test results."
    },
    "Obesity": {
        "icon": "⚖️",
        "precautions": [
            "Create a calorie deficit through diet and exercise combined",
            "Increase daily physical activity gradually to 150+ minutes per week",
            "Eat smaller portions and practice mindful eating habits",
            "Reduce consumption of sugary drinks and processed foods",
            "Increase fiber intake through whole grains, fruits, and vegetables",
            "Consider behavioral therapy or support groups for sustainable weight loss"
        ],
        "diet_tips": "Focus on whole foods with high protein and fiber content. Limit fast food and sugary treats. Use smaller plates to control portion sizes. Drink plenty of water throughout the day instead of sugary beverages.",
        "when_to_see_doctor": "Schedule regular follow-ups to track weight and health metrics. Report any difficulty exercising or persistent hunger. Consider referral to a dietitian or weight management specialist for personalized guidance."
    },
    "Thyroid Disorder": {
        "icon": "🣀",
        "precautions": [
            "Take thyroid medication exactly as prescribed at the same time daily",
            "Get regular blood tests to monitor TSH and hormone levels",
            "Maintain consistent iodine intake through diet or supplements",
            "Manage stress as it can affect thyroid function",
            "Avoid excessive soy consumption which can interfere with thyroid medication",
            "Report symptoms of hypo or hyperthyroidism to your doctor"
        ],
        "diet_tips": "Consume adequate iodine from seafood, dairy, or iodized salt. Eat selenium-rich foods like Brazil nuts and fish. Include zinc from meat and legumes. Maintain consistent nutrient intake daily.",
        "when_to_see_doctor": "Report unexplained weight changes, fatigue, mood changes, or temperature sensitivity. Schedule regular TSH testing to ensure proper medication dosing and adjust as needed."
    },
    "Arthritis": {
        "icon": "🦵",
        "precautions": [
            "Engage in low-impact exercises like swimming or cycling regularly",
            "Apply heat or cold therapy to affected joints as needed",
            "Maintain healthy weight to reduce stress on joints",
            "Take anti-inflammatory medications as prescribed",
            "Use joint protection devices or aids to reduce strain",
            "Get adequate rest and balance activity with recovery"
        ],
        "diet_tips": "Consume anti-inflammatory foods like fatty fish, berries, and leafy greens. Include ginger and turmeric in your diet. Limit red meat, processed foods, and sugar. Stay hydrated daily.",
        "when_to_see_doctor": "Report increased joint pain, swelling, stiffness, or reduced mobility. Discuss medication adjustments and physical therapy options. Regular check-ups help prevent further joint damage."
    },
    "Cancer": {
        "icon": "🏥",
        "precautions": [
            "Attend all recommended cancer screening appointments",
            "Avoid tobacco and secondhand smoke completely",
            "Limit alcohol consumption to safe levels",
            "Maintain a healthy weight through proper diet and exercise",
            "Follow sun safety measures including sunscreen and protective clothing",
            "Follow your treatment plan and attend all medical appointments"
        ],
        "diet_tips": "Eat a diet rich in fruits, vegetables, whole grains, and lean proteins. Limit processed and red meat consumption. Avoid added sugars and refined carbohydrates. Maintain proper hydration throughout the day.",
        "when_to_see_doctor": "Report any unusual lumps, persistent symptoms, or changes in health status immediately. Attend all scheduled screenings and follow-up appointments. Discuss any side effects from treatment with your oncologist."
    },
    "Depression": {
        "icon": "🧠",
        "precautions": [
            "Take antidepressant medications as prescribed consistently",
            "Attend therapy or counseling sessions regularly",
            "Maintain regular exercise routine which helps improve mood",
            "Establish consistent sleep schedule and get 7-9 hours nightly",
            "Build and maintain social connections and support systems",
            "Avoid alcohol and recreational drugs that worsen depression"
        ],
        "diet_tips": "Eat omega-3 rich foods like fatty fish and flaxseed. Consume adequate B vitamins from whole grains and lean proteins. Include mood-boosting foods like dark chocolate. Avoid excess caffeine and sugar.",
        "when_to_see_doctor": "Seek immediate help if experiencing suicidal thoughts or severe symptoms. Report medication side effects or worsening symptoms to your psychiatrist. Regular check-ups help adjust treatment as needed."
    },
    "Alzheimer's Disease": {
        "icon": "🧠",
        "precautions": [
            "Engage in regular cognitive activities like puzzles and learning",
            "Maintain regular physical exercise for brain health",
            "Stay socially connected through regular interaction with family",
            "Keep medical conditions like hypertension and diabetes controlled",
            "Get quality sleep regularly and maintain good sleep hygiene",
            "Take medications as prescribed and attend regular medical check-ups"
        ],
        "diet_tips": "Follow a Mediterranean-style diet rich in vegetables, fruits, whole grains, and fish. Include antioxidant-rich foods like berries. Limit red meat and processed foods. Stay well-hydrated.",
        "when_to_see_doctor": "Report memory concerns, confusion, or behavioral changes early. Regular cognitive testing helps track progression. Work with a neurologist on early intervention and management strategies."
    },
    "Pneumonia": {
        "icon": "💨",
        "precautions": [
            "Get vaccinated against pneumococcus and influenza annually",
            "Avoid smoking and secondhand smoke exposure",
            "Practice good hand hygiene to prevent infection",
            "Avoid close contact with people who are sick",
            "Maintain adequate hydration during and after infection",
            "Get adequate rest to support immune system recovery"
        ],
        "diet_tips": "Consume immune-boosting foods like vitamin C sources, garlic, ginger, and lean proteins. Eat warm broths and soups for hydration. Include foods with zinc and selenium for immune support.",
        "when_to_see_doctor": "Seek medical care for persistent cough, shortness of breath, or fever lasting more than 3 days. Get vaccinated to prevent pneumonia and consult your doctor about risk factors."
    },
}


# Default precautions for diseases not specifically defined
DEFAULT_PRECAUTIONS = {
    "icon": "⚕️",
    "precautions": [
        "Consult with your healthcare provider regularly for monitoring",
        "Follow all prescribed treatment plans and medication schedules",
        "Maintain a healthy lifestyle through balanced diet and exercise",
        "Manage stress through relaxation techniques and meditation",
        "Get adequate sleep and maintain consistent sleep schedules",
        "Follow preventive care recommendations from your physician"
    ],
    "diet_tips": "Maintain a balanced diet with adequate fruits, vegetables, whole grains, lean proteins, and healthy fats. Stay well-hydrated with water. Avoid excessive processed foods, sugar, and sodium.",
    "when_to_see_doctor": "Contact your healthcare provider if you notice any unusual or persistent symptoms. Attend all scheduled check-ups and discuss any changes in your health or medication side effects."
}


def get_precautions_for_disease(disease_name: str) -> Dict:
    """
    Get precautions and health recommendations for a specific disease.
    
    Uses exact matching first, then attempts partial matching (case-insensitive).
    Falls back to DEFAULT_PRECAUTIONS for unknown diseases.
    
    Args:
        disease_name (str): Name of the disease to get precautions for
    
    Returns:
        dict: Dictionary containing icon, precautions, diet_tips, and when_to_see_doctor
              Returns DEFAULT_PRECAUTIONS if disease not found
    """
    if not disease_name:
        logger.warning("[PRECAUTIONS] Empty disease name provided")
        return DEFAULT_PRECAUTIONS
    
    disease_name = disease_name.strip()
    
    # Try exact match first
    if disease_name in DISEASE_PRECAUTIONS:
        logger.debug(f"[PRECAUTIONS] Found exact match for disease: {disease_name}")
        return DISEASE_PRECAUTIONS[disease_name]
    
    # Try case-insensitive exact match
    disease_name_lower = disease_name.lower()
    for disease_key in DISEASE_PRECAUTIONS.keys():
        if disease_key.lower() == disease_name_lower:
            logger.debug(f"[PRECAUTIONS] Found case-insensitive match: {disease_name} -> {disease_key}")
            return DISEASE_PRECAUTIONS[disease_key]
    
    # Try partial match
    for disease_key in DISEASE_PRECAUTIONS.keys():
        if disease_name_lower in disease_key.lower() or disease_key.lower() in disease_name_lower:
            logger.info(f"[PRECAUTIONS] Found partial match: {disease_name} -> {disease_key}")
            return DISEASE_PRECAUTIONS[disease_key]
    
    # Fall back to default precautions
    logger.debug(f"[PRECAUTIONS] No match found for disease: {disease_name}. Using DEFAULT_PRECAUTIONS")
    return DEFAULT_PRECAUTIONS


def get_precautions_for_predictions(predictions: List[Dict]) -> List[Dict]:
    """
    Enrich a list of predictions with precaution data for High and Medium risk diseases.
    
    This function takes a list of prediction dictionaries and adds a 'precaution_data' key.
    For High and Medium risk diseases, it includes the relevant precautions.
    For Low risk diseases, precaution_data is set to None.
    
    Args:
        predictions (list): List of prediction dictionaries, each containing:
                           - disease (str): Disease name
                           - risk (str): Risk level ('High', 'Medium', 'Low')
                           - confidence (float): Confidence percentage
    
    Returns:
        list: Same predictions list with 'precaution_data' key added to each item
    """
    if not predictions:
        logger.warning("[PRECAUTIONS] Empty predictions list provided")
        return predictions
    
    enriched_predictions = []
    
    for prediction in predictions:
        try:
            disease_name = prediction.get('disease', 'Unknown')
            risk_level = prediction.get('risk', 'Low')
            
            # Only add precaution data for High and Medium risk diseases
            if risk_level in ['High', 'Medium']:
                precaution_data = get_precautions_for_disease(disease_name)
                prediction['precaution_data'] = precaution_data
                logger.debug(
                    f"[PRECAUTIONS] Added precaution data for {risk_level}-risk disease: {disease_name}"
                )
            else:
                # Low risk diseases don't get precaution data
                prediction['precaution_data'] = None
            
            enriched_predictions.append(prediction)
        
        except Exception as e:
            logger.error(
                f"[PRECAUTIONS] Error enriching prediction for disease '{prediction.get('disease', 'Unknown')}': {str(e)}",
                exc_info=True
            )
            # Still add the prediction but without precaution data
            prediction['precaution_data'] = None
            enriched_predictions.append(prediction)
    
    logger.info(
        f"[PRECAUTIONS] Enhanced {len(enriched_predictions)} predictions with precaution data"
    )
    
    return enriched_predictions
