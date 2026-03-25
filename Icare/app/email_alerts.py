"""
Email Alert System for High-Risk Disease Predictions
Sends professional HTML and plain text emails when high-risk diseases are detected.
"""

import logging
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from datetime import datetime

logger = logging.getLogger(__name__)


def _determine_risk_title(risk_diseases):
    has_high = any(d.get('risk') == 'High' for d in risk_diseases)
    has_medium = any(d.get('risk') == 'Medium' for d in risk_diseases)

    if has_high and has_medium:
        return 'HIGH & MEDIUM'
    elif has_high:
        return 'HIGH'
    elif has_medium:
        return 'MEDIUM'
    return 'LOW'


def send_risk_alert(user, analysis_result, risk_diseases, max_attempts=3):
    """
    Send an email alert when high-risk and/or medium-risk diseases are detected.

    Args:
        user (User): Django User object for the recipient
        analysis_result (AnalysisResult): The AnalysisResult model instance
        risk_diseases (list): List of disease dictionaries with risk levels
        max_attempts (int): Number of retry attempts for sending email

    Returns:
        tuple: (success: bool, attempts: int)
    """
    if not risk_diseases:
        logger.warning('[EMAIL_ALERT] No risk diseases provided for alert.')
        return False, 0

    valid = any(d.get('risk') in ['High', 'Medium'] for d in risk_diseases)
    if not valid:
        logger.warning('[EMAIL_ALERT] Provided diseases are not medium/high risk, skipping email.')
        return False, 0

    recipient_email = user.email
    sender_email = settings.DEFAULT_FROM_EMAIL
    risk_title = _determine_risk_title(risk_diseases)

    disease_list = ', '.join([d['disease'] for d in risk_diseases[:3]])
    if len(risk_diseases) > 3:
        disease_list += f", +{len(risk_diseases) - 3} more"

    subject = f"⚠️ {risk_title}-RISK HEALTH ALERT - Immediate Action Required: {disease_list}"
    plain_text = _generate_plain_text_email(user, analysis_result, risk_diseases, risk_title)
    html_content = _generate_html_email(user, analysis_result, risk_diseases, risk_title)

    for attempt in range(1, max_attempts + 1):
        try:
            logger.info(
                f"[EMAIL_ALERT] Attempt {attempt}/{max_attempts} for {risk_title}-risk alert to {recipient_email}"
            )

            email = EmailMultiAlternatives(
                subject=subject,
                body=plain_text,
                from_email=sender_email,
                to=[recipient_email]
            )

            email.attach_alternative(html_content, 'text/html')
            email.send(fail_silently=False)

            logger.info(
                f"[EMAIL_ALERT] ✓ {risk_title}-risk alert email sent successfully to {recipient_email} "
                f"(Analysis ID: {analysis_result.id}, attempt {attempt})"
            )
            return True, attempt

        except Exception as e:
            logger.error(
                f"[EMAIL_ALERT] ✗ Attempt {attempt} failed to send {risk_title}-risk email to {recipient_email}: {str(e)}",
                exc_info=True
            )
            if attempt == max_attempts:
                logger.error(f"[EMAIL_ALERT] All {max_attempts} attempts failed.")
                return False, attempt

    return False, max_attempts


def send_high_risk_alert(user, analysis_result, high_risk_diseases):
    """Backward-compatible wrapper for high-risk-only alerts."""
    return send_risk_alert(user, analysis_result, high_risk_diseases)



def _generate_plain_text_email(user, analysis_result, risk_diseases, risk_title='HIGH'):
    """
    Generate plain text version of the risk alert email.
    
    Args:
        user (User): Django User object
        analysis_result (AnalysisResult): The AnalysisResult model instance
        risk_diseases (list): List of disease dictionaries
        risk_title (str): 'HIGH', 'MEDIUM' or 'HIGH & MEDIUM'

    Returns:
        str: Plain text email content
    """
    disease_details = "\n".join([
        f"  • {d['disease']}: {d['confidence']}% confidence, Risk: {d['risk']}"
        for d in risk_diseases
    ])
    
    plain_text = f"""
IMPORTANT: {risk_title}-RISK HEALTH CONDITIONS DETECTED

Dear {user.first_name or user.email},

Your recent medical analysis has detected HIGH-RISK health conditions requiring immediate attention.

HIGH-RISK DISEASES IDENTIFIED:
{disease_details}

RECOMMENDED IMMEDIATE ACTIONS:
1. Consult with your primary care physician immediately
2. Do not delay - schedule an appointment today
3. Bring this alert and analysis results to your doctor
4. Follow-up testing may be required based on your condition
5. Keep all symptoms documented for your medical team
6. Seek emergency care if symptoms worsen

ANALYSIS DETAILS:
- Analysis ID: {analysis_result.id}
- Analysis Date: {analysis_result.created_at.strftime('%Y-%m-%d %H:%M:%S')}
- Total Diseases Analyzed: {analysis_result.total_diseases_analyzed}
- Average Confidence: {analysis_result.average_confidence:.1f}%

IMPORTANT MEDICAL DISCLAIMER:
This analysis is provided for informational purposes only and should not be used as a substitute 
for professional medical advice, diagnosis, or treatment. Please consult with a qualified healthcare 
provider for accurate diagnosis and appropriate treatment recommendations. Do not delay seeking 
professional medical care based on this analysis.

If you have any questions or concerns, please contact our support team.

Best regards,
ICARE Medical Prediction System
"""
    
    return plain_text


def _generate_html_email(user, analysis_result, risk_diseases, risk_title='HIGH'):
    """
    Generate professional HTML version of the risk alert email.
    
    Args:
        user (User): Django User object
        analysis_result (AnalysisResult): The AnalysisResult model instance
        risk_diseases (list): List of disease dictionaries
        risk_title (str): 'HIGH', 'MEDIUM' or 'HIGH & MEDIUM'
    
    Returns:
        str: HTML email content with styling
    """
    # Generate disease rows for the table
    disease_rows = ""
    for disease in risk_diseases:
        confidence = disease.get('confidence', 0)
        disease_name = disease.get('disease', 'Unknown')
        risk_level = disease.get('risk', 'Unknown')
        
        # Color code for risk level
        risk_color = "#dc2626" if risk_level == "High" else "#ea580c"
        
        disease_rows += f"""
        <tr>
            <td style="padding: 12px; border-bottom: 1px solid #e5e7eb;">
                <strong style="color: #1f2937;">{disease_name}</strong>
            </td>
            <td style="padding: 12px; border-bottom: 1px solid #e5e7eb; text-align: center;">
                <span style="font-weight: bold; color: #1f2937;">{confidence}%</span>
            </td>
            <td style="padding: 12px; border-bottom: 1px solid #e5e7eb; text-align: center;">
                <span style="background-color: {risk_color}; color: white; padding: 4px 12px; 
                           border-radius: 12px; font-weight: bold; font-size: 12px;">
                    {risk_level}
                </span>
            </td>
        </tr>
        """
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                line-height: 1.6;
                color: #374151;
                background-color: #f9fafb;
                margin: 0;
                padding: 0;
            }}
            .email-container {{
                max-width: 600px;
                margin: 0 auto;
                background-color: #ffffff;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            }}
            .header {{
                background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%);
                color: white;
                padding: 24px;
                text-align: center;
            }}
            .header-icon {{
                font-size: 48px;
                margin-bottom: 12px;
            }}
            .header h1 {{
                margin: 0;
                font-size: 24px;
                font-weight: bold;
            }}
            .header p {{
                margin: 8px 0 0 0;
                font-size: 14px;
                opacity: 0.9;
            }}
            .content {{
                padding: 24px;
            }}
            .greeting {{
                font-size: 16px;
                margin-bottom: 16px;
                color: #1f2937;
            }}
            .alert-box {{
                background-color: #fee2e2;
                border-left: 4px solid #dc2626;
                padding: 16px;
                margin-bottom: 20px;
                border-radius: 4px;
            }}
            .alert-box p {{
                margin: 0;
                color: #7f1d1d;
                font-weight: 500;
            }}
            .section-title {{
                font-size: 18px;
                font-weight: bold;
                color: #1f2937;
                margin-top: 20px;
                margin-bottom: 12px;
                border-bottom: 2px solid #3b82f6;
                padding-bottom: 8px;
            }}
            .disease-table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
                background-color: #f9fafb;
                border-radius: 4px;
                overflow: hidden;
            }}
            .disease-table th {{
                background-color: #3b82f6;
                color: white;
                padding: 12px;
                text-align: left;
                font-weight: bold;
                font-size: 13px;
            }}
            .disease-table tr:last-child td {{
                border-bottom: none;
            }}
            .action-steps {{
                list-style: none;
                padding: 0;
                margin: 0;
            }}
            .action-steps li {{
                padding: 10px 0;
                border-bottom: 1px solid #e5e7eb;
                display: flex;
                align-items: flex-start;
            }}
            .action-steps li:last-child {{
                border-bottom: none;
            }}
            .action-steps li:before {{
                content: "✓";
                color: #dc2626;
                font-weight: bold;
                margin-right: 12px;
                font-size: 16px;
                min-width: 24px;
            }}
            .info-box {{
                background-color: #eff6ff;
                border-left: 4px solid #3b82f6;
                padding: 16px;
                margin-bottom: 20px;
                border-radius: 4px;
            }}
            .info-box p {{
                margin: 4px 0;
                font-size: 13px;
                color: #1e40af;
            }}
            .info-box strong {{
                color: #1e3a8a;
            }}
            .disclaimer {{
                background-color: #fef3c7;
                border-left: 4px solid #f59e0b;
                padding: 16px;
                margin-bottom: 20px;
                border-radius: 4px;
            }}
            .disclaimer p {{
                margin: 0;
                font-size: 12px;
                color: #78350f;
                line-height: 1.5;
            }}
            .footer {{
                background-color: #f3f4f6;
                padding: 16px;
                text-align: center;
                border-top: 1px solid #e5e7eb;
                font-size: 12px;
                color: #6b7280;
            }}
            .footer p {{
                margin: 4px 0;
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <!-- Header -->
            <div class="header">
                <div class="header-icon">⚠️</div>
                <h1>{risk_title}-RISK HEALTH ALERT</h1>
                <p>Immediate Medical Attention Required</p>
            </div>
            
            <!-- Content -->
            <div class="content">
                <p class="greeting">Dear {user.first_name or user.email},</p>
                
                <div class="alert-box">
                    <p>Your recent medical analysis has detected <strong>{risk_title}-RISK health conditions</strong> requiring immediate attention. Please consult with your healthcare provider as soon as possible.</p>
                </div>
                
                <!-- Disease Table -->
                <div class="section-title">🏥 High-Risk Diseases Identified</div>
                <table class="disease-table">
                    <thead>
                        <tr>
                            <th>Disease</th>
                            <th style="text-align: center;">Confidence</th>
                            <th style="text-align: center;">Risk Level</th>
                        </tr>
                    </thead>
                    <tbody>
                        {disease_rows}
                    </tbody>
                </table>
                
                <!-- Action Steps -->
                <div class="section-title">📋 Recommended Immediate Actions</div>
                <ul class="action-steps">
                    <li>Consult with your primary care physician immediately</li>
                    <li>Schedule an appointment today - do not delay</li>
                    <li>Bring this alert and analysis results to your doctor</li>
                    <li>Follow-up testing may be required based on your condition</li>
                    <li>Keep all symptoms documented for your medical team</li>
                    <li>Seek emergency care if symptoms worsen</li>
                </ul>
                
                <!-- Analysis Details -->
                <div class="section-title">📊 Analysis Details</div>
                <div class="info-box">
                    <p><strong>Analysis ID:</strong> {analysis_result.id}</p>
                    <p><strong>Analysis Date:</strong> {analysis_result.created_at.strftime('%B %d, %Y at %I:%M %p')}</p>
                    <p><strong>Total Diseases Analyzed:</strong> {analysis_result.total_diseases_analyzed}</p>
                    <p><strong>Average Confidence:</strong> {analysis_result.average_confidence:.1f}%</p>
                </div>
                
                <!-- Medical Disclaimer -->
                <div class="disclaimer">
                    <p><strong>IMPORTANT MEDICAL DISCLAIMER:</strong> This analysis is provided for informational purposes only and should not be used as a substitute for professional medical advice, diagnosis, or treatment. Results are based on machine learning analysis of your provided medical data. Please consult with a qualified healthcare provider for accurate diagnosis and appropriate treatment recommendations. Do not delay seeking professional medical care based on this analysis. In case of medical emergency, call emergency services immediately.</p>
                </div>
                
                <p style="text-align: center; margin-top: 24px; margin-bottom: 0; font-size: 13px; color: #6b7280;">
                    If you have any questions or concerns, please contact our support team.
                </p>
            </div>
            
            <!-- Footer -->
            <div class="footer">
                <p><strong>ICARE Medical Prediction System</strong></p>
                <p>Advanced Healthcare Analytics Platform</p>
                <p style="margin-top: 8px; border-top: 1px solid #d1d5db; padding-top: 8px;">© 2025 ICARE. All rights reserved. This is an automated alert message - do not reply to this email.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_content
