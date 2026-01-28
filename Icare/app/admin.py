from django.contrib import admin
from .models import Patients, MedicalReport, AnalysisResult

# Register your models here.
admin.site.register(Patients)


@admin.register(MedicalReport)
class MedicalReportAdmin(admin.ModelAdmin):
    list_display = ('patient_name', 'user', 'created_at')
    search_fields = ('patient_name', 'user__email')
    list_filter = ('created_at',)
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'


@admin.register(AnalysisResult)
class AnalysisResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'average_confidence', 'total_patients', 'created_at')
    search_fields = ('user__email', 'medical_report__patient_name')
    list_filter = ('created_at', 'average_confidence')
    readonly_fields = ('created_at', 'updated_at', 'average_confidence')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Report Information', {
            'fields': ('medical_report', 'user')
        }),
        ('Statistics', {
            'fields': ('total_patients', 'total_diseases_analyzed', 'high_risk_count', 
                      'medium_risk_count', 'low_risk_count', 'average_confidence')
        }),
        ('Data', {
            'fields': ('predictions_json',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )