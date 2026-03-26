# EmailJS Integration Setup Guide

This guide explains how to configure EmailJS for sending health alert emails in the ICARE system.

## Overview

EmailJS has been integrated into the email alert system to provide reliable and professional email delivery. The system uses:
- **Service ID**: `service_1dt5q2f`
- **Template ID**: `template_a6f6q6q`
- **EmailJS API**: `https://api.emailjs.com/api/v1.0/email/send`

## Prerequisites

1. An EmailJS account (free tier available at https://www.emailjs.com)
2. Your EmailJS Public Key

## Step 1: Get Your EmailJS Public Key

1. Go to [EmailJS Dashboard](https://dashboard.emailjs.com)
2. Navigate to **Account** → **API Keys**
3. Copy your **Public Key**

## Step 2: Configure Environment Variables

### Option A: Using .env file (Recommended for Development)

Create or update your `.env` file in the project root:

```env
EMAILJS_PUBLIC_KEY=your_public_key_here
```

**Note**: Add `.env` to `.gitignore` to prevent exposing sensitive keys:
```
.env
.env.local
*.env
```

### Option B: Direct Settings Configuration

Update `Icare/settings.py` if not using .env:

```python
EMAILJS_PUBLIC_KEY = 'your_public_key_here'
```

## Step 3: Verify EmailJS Template Configuration

Your EmailJS template should have the following variables (as shown in the template screenshot):

### Template Variables:
- `{{to_email}}` - Recipient email address
- `{{to_name}}` - Recipient name
- `{{patient_name}}` - Patient's first name
- `{{patient_id}}` - Patient's ID
- `{{risk_level}}` - Risk level (HIGH, MEDIUM, HIGH & MEDIUM)
- `{{disease_name}}` - Detected disease name(s)
- `{{diseases_detected}}` - Formatted list of all detected diseases
- `{{action_steps}}` - Recommended actions for the patient
- `{{alert_time}}` - Time the alert was generated
- `{{analysis_id}}` - Analysis result ID
- `{{total_diseases}}` - Total number of diseases analyzed
- `{{average_confidence}}` - Average confidence percentage
- `{{subject}}` - Email subject line

### Template Structure:
Your EmailJS template should follow this structure:

```
Subject: {{subject}}

Hello {{to_name}},

A {{risk_level}}-risk health condition has been detected for your patient {{patient_name}} (ID: {{patient_id}}).

DETECTED CONDITIONS:
{{disease_name}}

{{diseases_detected}}

RECOMMENDED ACTIONS:
{{action_steps}}

ANALYSIS DETAILS:
- Analysis ID: {{analysis_id}}
- Alert Time: {{alert_time}}
- Total Diseases Analyzed: {{total_diseases}}
- Average Confidence: {{average_confidence}}

[Add your custom HTML/formatting as needed]
```

## Step 4: Python Dependencies

Ensure `requests` is in your requirements.txt:

```bash
pip install requests
```

The following has been added to `requirements.txt`:
```
requests>=2.28.0
```

## Step 5: Install Dependencies

```bash
pip install -r requirements.txt
```

## Code Implementation

The email alert system has been updated in `app/email_alerts.py`:

### Main Function

```python
def send_risk_alert(user, analysis_result, risk_diseases, max_attempts=3):
    """
    Send an email alert via EmailJS when high-risk and/or medium-risk diseases are detected.
    
    Args:
        user (User): Django User object for the recipient
        analysis_result (AnalysisResult): The AnalysisResult model instance
        risk_diseases (list): List of disease dictionaries with risk levels
        max_attempts (int): Number of retry attempts for sending email
    
    Returns:
        tuple: (success: bool, attempts: int)
    """
```

### Usage Example

```python
from app.email_alerts import send_risk_alert

# In your views.py or signal handlers
success, attempts = send_risk_alert(
    user=request.user,
    analysis_result=analysis_result,
    risk_diseases=high_risk_diseases
)

if success:
    print(f"Email sent successfully in {attempts} attempt(s)")
else:
    print(f"Failed to send email after {attempts} attempts")
```

## Features

✅ **Auto-retry mechanism** - Retries up to 3 times if delivery fails
✅ **Comprehensive logging** - Detailed logs for troubleshooting
✅ **Template variables** - All patient and analysis data automatically formatted
✅ **Error handling** - Graceful error handling with timeout protection
✅ **Professional styling** - Uses EmailJS template for consistent formatting

## Logging

All email sending attempts are logged to `logger.info()` and `logger.error()` with the `[EMAIL_ALERT]` prefix.

### Example Log Output:

```
[EMAIL_ALERT] Attempt 1/3 for HIGH-risk alert to patient@example.com
[EMAIL_ALERT] ✓ HIGH-risk alert email sent successfully via EmailJS to patient@example.com (Analysis ID: 123, attempt 1)
```

## Troubleshooting

### Issue: "EMAILJS_PUBLIC_KEY not configured"

**Solution**: Ensure your `.env` file has:
```env
EMAILJS_PUBLIC_KEY=your_actual_public_key
```

### Issue: EmailJS returns 400 error

**Possible causes**:
- Invalid template variables (check variable names match exactly)
- EmailJS service/template IDs don't match
- Public key is incorrect

**Solution**: 
1. Verify Service ID: `service_1dt5q2f`
2. Verify Template ID: `template_a6f6q6q`
3. Check your public key in EmailJS dashboard
4. Review EmailJS template variable names

### Issue: Timeout errors

**Solution**: Check your internet connection and EmailJS service status at https://status.emailjs.com

### Issue: Emails not being sent

**Debugging steps**:
1. Check Django logs for `[EMAIL_ALERT]` entries
2. Verify patient has valid email address
3. Check risk_diseases list contains High or Medium risk items
4. Test manually:

```python
from django.contrib.auth.models import User
from app.models import AnalysisResult
from app.email_alerts import send_risk_alert

user = User.objects.first()
analysis = AnalysisResult.objects.first()
risk_diseases = [
    {'disease': 'Diabetes', 'confidence': 85, 'risk': 'High'}
]

success, attempts = send_risk_alert(user, analysis, risk_diseases)
print(f"Success: {success}, Attempts: {attempts}")
```

## Security Notes

⚠️ **Important**:
- Never commit your `.env` file with `EMAILJS_PUBLIC_KEY`
- Use environment variables in production
- Keep your EmailJS API keys confidential
- The public key provided is safe to expose (it's meant to be public for frontend use)

## EmailJS Dashboard

To manage your emails and view sending statistics:
1. Visit https://dashboard.emailjs.com
2. Navigate to **Email Activity** to see sent emails
3. Check **Contact Form** for any blocking issues

## Additional Resources

- [EmailJS Documentation](https://www.emailjs.com/docs/)
- [EmailJS API Reference](https://www.emailjs.com/docs/rest-api/send/)
- [EmailJS Templates Guide](https://www.emailjs.com/docs/service/gmail/)

## Next Steps

1. ✅ Add your public key to `.env`
2. ✅ Install dependencies: `pip install -r requirements.txt`
3. ✅ Restart Django development server
4. ✅ Test by triggering a high-risk analysis prediction
5. ✅ Check email inbox for alert

---

**Last Updated**: March 2026
**Integration Status**: ✅ Active (using EmailJS API v1.0)
