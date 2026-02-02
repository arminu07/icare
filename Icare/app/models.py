from django.db import models
from django.contrib.auth.models import User
import json

# Create your models here.
class Patients(models.Model):
    name=models.CharField(max_length=100)
    password=models.CharField(max_length=10)
    phone=models.IntegerField(blank=True, null=True)
    email=models.EmailField()
    location=models.CharField(max_length=100, blank=True, null=True)
    image=models.FileField(upload_to='profile',blank=True,null=True)

    def __str__(self):
        return  self.name


class MedicalReport(models.Model):
    """Model to store medical report uploads with detailed records"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='medical_reports')
    patient_name = models.CharField(max_length=200, blank=True)
    csv_file = models.FileField(upload_to='medical_reports/')
    details = models.TextField(blank=True, null=True)
    
    # Detailed medical information
    age = models.IntegerField(blank=True, null=True)
    gender = models.CharField(max_length=20, blank=True, null=True)
    blood_pressure = models.CharField(max_length=20, blank=True, null=True)
    cholesterol = models.CharField(max_length=20, blank=True, null=True)
    glucose = models.CharField(max_length=20, blank=True, null=True)
    
    # Additional clinical notes
    clinical_notes = models.TextField(blank=True, null=True)
    medications = models.TextField(blank=True, null=True, help_text="Current medications")
    allergies = models.TextField(blank=True, null=True)
    family_history = models.TextField(blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Report by {self.user.email} - {self.created_at.strftime('%Y-%m-%d')}"
    
    def get_medical_summary(self):
        """Get a summary of medical data from CSV"""
        return {
            'patient_name': self.patient_name,
            'age': self.age,
            'gender': self.gender,
            'blood_pressure': self.blood_pressure,
            'cholesterol': self.cholesterol,
            'glucose': self.glucose,
            'clinical_notes': self.clinical_notes,
            'medications': self.medications,
            'allergies': self.allergies,
            'family_history': self.family_history,
        }


class AnalysisResult(models.Model):
    """Model to store disease prediction results with detailed records"""
    RISK_CHOICES = [
        ('High', 'High Risk'),
        ('Medium', 'Medium Risk'),
        ('Low', 'Low Risk'),
    ]
    
    medical_report = models.OneToOneField(MedicalReport, on_delete=models.CASCADE, related_name='analysis_result')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='analysis_results')
    
    # Summary statistics
    total_patients = models.IntegerField(default=0)
    total_diseases_analyzed = models.IntegerField(default=0)
    high_risk_count = models.IntegerField(default=0)
    medium_risk_count = models.IntegerField(default=0)
    low_risk_count = models.IntegerField(default=0)
    average_confidence = models.FloatField(default=0.0)
    
    # Predictions stored as JSON for detailed records
    predictions_json = models.JSONField(default=dict)
    
    # Clinical recommendations
    recommendations = models.TextField(blank=True, null=True, help_text="AI-generated clinical recommendations")
    follow_up_actions = models.TextField(blank=True, null=True, help_text="Recommended follow-up actions")
    
    # Metadata for audit trail
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    analysis_duration = models.FloatField(default=0.0, help_text="Analysis time in seconds")
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Analysis for {self.medical_report} - {self.average_confidence:.1f}% confidence"
    
    def get_top_predictions(self, limit=15):
        """Get top N predictions sorted by confidence"""
        predictions = self.predictions_json.get('predictions', [])
        return sorted(predictions, key=lambda x: x.get('confidence', 0), reverse=True)[:limit]
    
    def get_high_risk_diseases(self):
        """Get all high-risk diseases"""
        predictions = self.predictions_json.get('predictions', [])
        return [p for p in predictions if p.get('risk') == 'High']
    
    def get_medium_risk_diseases(self):
        """Get all medium-risk diseases"""
        predictions = self.predictions_json.get('predictions', [])
        return [p for p in predictions if p.get('risk') == 'Medium']
    
    def get_low_risk_diseases(self):
        """Get all low-risk diseases"""
        predictions = self.predictions_json.get('predictions', [])
        return [p for p in predictions if p.get('risk') == 'Low']
    
    def get_full_medical_record(self):
        """Get complete medical record for archival"""
        return {
            'analysis_id': self.id,
            'patient_report': self.medical_report.get_medical_summary(),
            'predictions': self.predictions_json,
            'recommendations': self.recommendations,
            'follow_up_actions': self.follow_up_actions,
            'created_at': self.created_at.isoformat(),
            'analysis_duration': self.analysis_duration,
        }
