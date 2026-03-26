# EmailJS Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### Step 1: Get Your EmailJS Public Key (2 minutes)

1. Visit: https://www.emailjs.com/
2. Sign up or login to your account
3. Go to **Account** → **API Keys**
4. Copy your **Public Key**

### Step 2: Configure Your Project (1 minute)

**Option A - Recommended (Using .env file)**:

1. Create a `.env` file in your project root (same level as `manage.py`):
   ```
   EMAILJS_PUBLIC_KEY=your_public_key_here_paste_your_actual_key
   ```

2. Add `.env` to `.gitignore`:
   ```bash
   echo ".env" >> .gitignore
   ```

**Option B - Direct Configuration** (Not recommended for production):

Edit `Icare/settings.py` and update:
```python
EMAILJS_PUBLIC_KEY = 'your_public_key_here'
```

### Step 3: Install Dependencies (1 minute)

```bash
pip install -r requirements.txt
```

### Step 4: Restart Django Server (30 seconds)

```bash
# Stop current server (Ctrl+C)
# Then restart:
python manage.py runserver
```

### Step 5: Test It! (30 seconds)

Trigger a high-risk analysis prediction and check:
- ✅ Patient's email inbox for the alert
- ✅ Django console logs for `[EMAIL_ALERT]` messages

---

## 📋 Configuration Reference

| Setting | Value |
|---------|-------|
| **Service ID** | `service_1dt5q2f` ✅ (Already configured) |
| **Template ID** | `template_a6f6q6q` ✅ (Already configured) |
| **API Endpoint** | `https://api.emailjs.com/api/v1.0/email/send` ✅ (Already configured) |
| **Public Key** | 🔴 **YOU NEED TO ADD THIS** → See Step 2 |

---

## ⚙️ What Was Configured For You

✅ **Backend Code** - Uses EmailJS API for sending emails
✅ **Email Logic** - Automatic retry mechanism (3 attempts)
✅ **Template Variables** - All patient data automatically formatted
✅ **Error Handling** - Comprehensive logging and error recovery
✅ **Dependencies** - `requests` library added

---

## 🧪 Test Email Sending

### Via Django Shell:

```python
python manage.py shell

# Then run:
from django.contrib.auth.models import User
from app.models import AnalysisResult
from app.email_alerts import send_risk_alert

# Get a test user and analysis
user = User.objects.first()
analysis = AnalysisResult.objects.first()

# Create test risk diseases
risk_diseases = [
    {
        'disease': 'Diabetes',
        'confidence': 85,
        'risk': 'High'
    },
    {
        'disease': 'Hypertension',
        'confidence': 72,
        'risk': 'Medium'
    }
]

# Send test email
success, attempts = send_risk_alert(user, analysis, risk_diseases)
print(f"Email sent: {success} (Attempts: {attempts})")

# Exit shell
exit()
```

### Check Logs:

Watch the Django console for output like:
```
[EMAIL_ALERT] Attempt 1/3 for HIGH & MEDIUM-risk alert to patient@example.com
[EMAIL_ALERT] ✓ HIGH & MEDIUM-risk alert email sent successfully via EmailJS...
```

---

## 📊 Monitor Email Delivery

1. Go to: https://dashboard.emailjs.com
2. Navigate to **Email Activity**
3. View:
   - ✅ Successful sends
   - ⏱️ Delivery time
   - 📈 Bounce rates
   - 💬 Email content

---

## 🔍 Troubleshooting

### ❌ Emails not sending?

1. **Check if public key is set:**
   ```python
   python manage.py shell
   from django.conf import settings
   print(settings.EMAILJS_PUBLIC_KEY)
   # Should print your key, not 'your_public_key_here'
   exit()
   ```

2. **Check Django logs** for `[EMAIL_ALERT]` errors

3. **Verify EmailJS dashboard**:
   - Service ID correct: `service_1dt5q2f`
   - Template ID correct: `template_a6f6q6q`
   - Public key matches your account

4. **Test network connection**:
   ```bash
   ping emailjs.com
   ```

### ❌ "Module not found: requests"?

```bash
pip install requests
pip install -r requirements.txt
```

### ❌ Wrong email template variables?

Make sure your EmailJS template has all these variables:
- `{{to_email}}`
- `{{to_name}}`
- `{{patient_name}}`
- `{{patient_id}}`
- `{{risk_level}}`
- `{{disease_name}}`
- `{{diseases_detected}}`
- `{{action_steps}}`
- `{{alert_time}}`
- `{{analysis_id}}`
- `{{total_diseases}}`
- `{{average_confidence}}`
- `{{subject}}`

---

## 📚 Full Documentation

For complete details, see:
- [`EMAILJS_SETUP.md`](EMAILJS_SETUP.md) - Comprehensive setup guide
- [`EMAILJS_INTEGRATION_SUMMARY.md`](EMAILJS_INTEGRATION_SUMMARY.md) - What was changed
- [`app/email_alerts.py`](../app/email_alerts.py) - Implementation code

---

## ✅ Checklist

- [ ] EmailJS public key obtained from dashboard
- [ ] `.env` file created with public key (or configured in settings.py)
- [ ] `.env` added to `.gitignore`
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] Django server restarted
- [ ] Test email sent successfully
- [ ] Django logs show `[EMAIL_ALERT] ✓` message
- [ ] Email received in patient inbox

---

## 🎉 You're Ready!

Once the above checklist is complete, your ICARE system will automatically send professional health alert emails whenever high-risk or medium-risk diseases are detected!

**Questions?** Check the full documentation in `EMAILJS_SETUP.md`

---

**Status**: ✅ Ready to Deploy
**Last Updated**: March 26, 2026
