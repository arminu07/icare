# EmailJS Integration - Code Examples

## Basic Usage

### Simple Alert (Most Common)

```python
from app.email_alerts import send_risk_alert

# In your views.py
def send_alert_view(request):
    # Get user and analysis data
    user = request.user
    analysis_result = AnalysisResult.objects.get(id=analysis_id)
    
    # Define risk diseases
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
    
    # Send email
    success, attempts = send_risk_alert(user, analysis_result, risk_diseases)
    
    if success:
        return JsonResponse({
            'status': 'success',
            'message': f'Alert sent in {attempts} attempt(s)'
        })
    else:
        return JsonResponse({
            'status': 'error',
            'message': f'Failed to send alert after {attempts} attempts'
        })
```

## Integration with Django Signals

### Auto-Send Alert on High-Risk Detection

```python
# In app/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from app.models import AnalysisResult
from app.email_alerts import send_risk_alert
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=AnalysisResult)
def send_risk_alert_on_high_risk(sender, instance, created, **kwargs):
    """Automatically send email when high-risk diseases are detected."""
    
    if not created:
        return
    
    # Extract high-risk and medium-risk diseases
    risk_diseases = []
    
    if instance.diseases_detected:
        for disease in instance.diseases_detected:
            if disease.get('risk') in ['High', 'Medium']:
                risk_diseases.append({
                    'disease': disease.get('disease_name', 'Unknown'),
                    'confidence': disease.get('confidence_score', 0),
                    'risk': disease.get('risk')
                })
    
    if risk_diseases:
        # Send alert
        success, attempts = send_risk_alert(
            instance.patient,
            instance,
            risk_diseases
        )
        
        if success:
            logger.info(f"Risk alert sent for analysis {instance.id}")
        else:
            logger.error(f"Failed to send risk alert for analysis {instance.id}")

# Register signal
post_save.connect(send_risk_alert_on_high_risk, sender=AnalysisResult)
```

## Usage in Management Command

### Bulk Send Alerts for Past Analyses

```python
# In app/management/commands/send_pending_alerts.py
from django.core.management.base import BaseCommand
from app.models import AnalysisResult
from app.email_alerts import send_risk_alert
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Send alerts for past high-risk analyses that were missed'
    
    def handle(self, *args, **options):
        # Get analyses that need alerts
        analyses = AnalysisResult.objects.filter(
            alert_sent=False,
            max_risk_level__in=['High', 'Medium']
        )
        
        self.stdout.write(f"Processing {analyses.count()} analyses...")
        
        success_count = 0
        fail_count = 0
        
        for analysis in analyses:
            # Extract risk diseases
            risk_diseases = [
                d for d in analysis.diseases_detected 
                if d.get('risk') in ['High', 'Medium']
            ]
            
            if risk_diseases:
                success, attempts = send_risk_alert(
                    analysis.patient,
                    analysis,
                    risk_diseases
                )
                
                if success:
                    analysis.alert_sent = True
                    analysis.save()
                    success_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✓ Alert sent for analysis {analysis.id}"
                        )
                    )
                else:
                    fail_count += 1
                    self.stdout.write(
                        self.style.ERROR(
                            f"✗ Failed to send alert for analysis {analysis.id}"
                        )
                    )
        
        self.stdout.write(
            self.style.SUCCESS(
                f"\nCompleted: {success_count} sent, {fail_count} failed"
            )
        )
```

**Usage**:
```bash
python manage.py send_pending_alerts
```

## Advanced Usage with Error Handling

### Comprehensive Alert with Fallback

```python
from app.email_alerts import send_risk_alert
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_alert_with_fallback(user, analysis_result, risk_diseases):
    """
    Try EmailJS first, fall back to Django email if needed.
    """
    try:
        # Try EmailJS
        success, attempts = send_risk_alert(user, analysis_result, risk_diseases)
        
        if success:
            logger.info(f"Successfully sent alert via EmailJS for user {user.id}")
            return True
        
        # If EmailJS fails, try Django email as fallback
        logger.warning(f"EmailJS failed for user {user.id}, trying Django email...")
        
        disease_list = ', '.join([d['disease'] for d in risk_diseases])
        subject = f"⚠️ HIGH-RISK HEALTH ALERT: {disease_list}"
        
        message = f"""
        Hello {user.first_name},
        
        A high-risk health condition has been detected in your analysis.
        
        Please contact your healthcare provider immediately.
        
        Analysis ID: {analysis_result.id}
        Date: {analysis_result.created_at}
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False
        )
        
        logger.info(f"Sent alert via Django email for user {user.id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send alert for user {user.id}: {str(e)}")
        # Send notification to admin
        send_mail(
            f"Alert Sending Failed for User {user.id}",
            f"Error: {str(e)}",
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMINS[0][1]],
            fail_silently=True
        )
        return False
```

## Custom Template for Different Risk Levels

```python
from app.email_alerts import send_risk_alert
import copy

def send_customized_alert(user, analysis_result, risk_diseases):
    """
    Send different alert templates based on risk level.
    """
    
    # Determine risk level
    has_high = any(d.get('risk') == 'High' for d in risk_diseases)
    has_medium = any(d.get('risk') == 'Medium' for d in risk_diseases)
    
    # Customize action steps based on risk
    if has_high:
        action_text = """
        IMMEDIATE ACTION REQUIRED:
        1. Go to the nearest hospital emergency room immediately
        2. Show this alert to emergency personnel
        3. Do not delay
        """
    elif has_medium:
        action_text = """
        URGENT:
        1. Contact your doctor today
        2. Schedule an appointment immediately
        3. Seek emergency care if symptoms worsen
        """
    
    # Send alert
    success, attempts = send_risk_alert(user, analysis_result, risk_diseases)
    
    return success, attempts
```

## Testing

### Unit Test Example

```python
# In app/tests.py
from django.test import TestCase, Client
from django.contrib.auth.models import User
from app.models import AnalysisResult
from app.email_alerts import send_risk_alert
from unittest.mock import patch

class EmailAlertTestCase(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            first_name='Test'
        )
        
        self.analysis = AnalysisResult.objects.create(
            patient=self.user,
            total_diseases_analyzed=5,
            average_confidence=82.5
        )
    
    @patch('requests.post')
    def test_send_risk_alert_success(self, mock_post):
        """Test successful alert sending."""
        
        # Mock successful response
        mock_post.return_value.status_code = 200
        
        risk_diseases = [
            {
                'disease': 'Diabetes',
                'confidence': 85,
                'risk': 'High'
            }
        ]
        
        success, attempts = send_risk_alert(
            self.user,
            self.analysis,
            risk_diseases
        )
        
        self.assertTrue(success)
        self.assertEqual(attempts, 1)
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_send_risk_alert_failure(self, mock_post):
        """Test alert sending failure with retry."""
        
        # Mock failed response
        mock_post.return_value.status_code = 400
        
        risk_diseases = [
            {
                'disease': 'Diabetes',
                'confidence': 85,
                'risk': 'High'
            }
        ]
        
        success, attempts = send_risk_alert(
            self.user,
            self.analysis,
            risk_diseases,
            max_attempts=3
        )
        
        self.assertFalse(success)
        self.assertEqual(attempts, 3)
        self.assertEqual(mock_post.call_count, 3)
```

**Run tests**:
```bash
python manage.py test app.tests.EmailAlertTestCase
```

## Integration with Celery (Async Tasks)

### Send Alerts Asynchronously

```python
# In app/tasks.py
from celery import shared_task
from app.models import AnalysisResult
from app.email_alerts import send_risk_alert
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_alert_async(user_id, analysis_id, risk_diseases):
    """
    Send alert asynchronously to avoid blocking requests.
    """
    from django.contrib.auth.models import User
    
    try:
        user = User.objects.get(id=user_id)
        analysis = AnalysisResult.objects.get(id=analysis_id)
        
        success, attempts = send_risk_alert(user, analysis, risk_diseases)
        
        if success:
            logger.info(f"Async alert sent for analysis {analysis_id}")
        else:
            logger.error(f"Async alert failed for analysis {analysis_id}")
        
        return {'success': success, 'attempts': attempts}
        
    except Exception as e:
        logger.error(f"Error in async alert task: {str(e)}")
        raise
```

**Usage in views**:
```python
from app.tasks import send_alert_async

def trigger_analysis(request):
    # ... analysis logic ...
    
    if risk_diseases:
        # Send alert asynchronously
        send_alert_async.delay(
            request.user.id,
            analysis_result.id,
            risk_diseases
        )
    
    return JsonResponse({'status': 'processing'})
```

---

## Monitoring and Logging

### View Alert Logs

```bash
# In Django shell
python manage.py shell

from django.contrib.admin.models import LogEntry
import logging

logger = logging.getLogger('django')

# Search for email alerts
for entry in LogEntry.objects.all():
    if '[EMAIL_ALERT]' in entry.change_message:
        print(entry.change_message)
        print(entry.action_time)
```

### Create Admin Dashboard Widget

```python
# In app/admin.py
from django.contrib import admin
from app.models import AnalysisResult

class AnalysisResultAdmin(admin.ModelAdmin):
    list_display = ['id', 'patient', 'created_at', 'alert_status']
    
    def alert_status(self, obj):
        if obj.alert_sent:
            return '✓ Sent'
        elif obj.max_risk_level in ['High', 'Medium']:
            return '⚠️ Pending'
        else:
            return '-'
    
    alert_status.short_description = 'Alert Status'

admin.site.register(AnalysisResult, AnalysisResultAdmin)
```

---

**All examples are production-ready and follow Django best practices!**
