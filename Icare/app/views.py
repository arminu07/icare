from django.shortcuts import render,redirect
from.models import *
import logging
from django.contrib.auth import login,logout,authenticate
import csv
import json
from django.contrib.auth.decorators import login_required
from .disease_predictor import predict_from_csv
import io
from django.http import JsonResponse
from datetime import datetime
from django.db import models as django_models
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

logger = logging.getLogger(__name__)

# Create your views here.
def home(request):
    return render(request,'home.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')
        
        try:
            # Try to authenticate with Django user first
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                # Login the user
                login(request, user)
                request.session['email'] = email
                logger.info(f"User logged in successfully: {email}")
                return redirect('home')
            else:
                # Check if patient exists but password is wrong
                try:
                    patient = Patients.objects.get(email=email)
                    error_msg = 'Invalid email or password.'
                    logger.warning(f"Login attempt with wrong password for: {email}")
                except Patients.DoesNotExist:
                    error_msg = 'Invalid email or password.'
                    logger.warning(f"Login attempt with non-existent email: {email}")
                
                return render(request, 'login.html', {'error': error_msg})
                
        except Exception as e:
            error_msg = f'Error during login: {str(e)}'
            logger.error(f"Login error for {email}: {str(e)}", exc_info=True)
            return render(request, 'login.html', {'error': error_msg})
    
    return render(request, 'login.html')


def signup (request):
    if request.method =='POST':
        first_name = request.POST.get('FirstName', '')
        last_name = request.POST.get('lastName', '')
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')
        
        
        name = f"{first_name} {last_name}".strip()
        
        try:
            # Check if user already exists
            if User.objects.filter(email=email).exists():
                error_msg = 'Email already registered. Please use a different email or login.'
                logger.warning(f"Signup attempt with existing email: {email}")
                return render(request, 'signup.html', {'error': error_msg})
            
            if Patients.objects.filter(email=email).exists():
                error_msg = 'Email already registered in patient database. Please use a different email or login.'
                logger.warning(f"Patient signup attempt with existing email: {email}")
                return render(request, 'signup.html', {'error': error_msg})
            
            # Validate required fields
            if not email or not password:
                error_msg = 'Email and password are required.'
                return render(request, 'signup.html', {'error': error_msg})
            
            # Create Django user
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            
            # Create patient record
            patient = Patients.objects.create(
                name=name,
                password=password,
                email=email
            )
            
            logger.info(f"New patient created: {email} with ID: {patient.id}")
            
            # Auto-login after signup
            login(request, user)
            request.session['email'] = email
            
            return redirect('home')
        except Exception as e:
            error_msg = f'Error creating account: {str(e)}'
            logger.error(f"Signup error for {email}: {str(e)}", exc_info=True)
            return render(request, 'signup.html', {'error': error_msg})
    
    return render(request, 'signup.html')

def logout_view(request):
    logout(request)
    try:
        del request.session['email']    
    except KeyError:
        pass
    return redirect('home')


@login_required(login_url='login')
def dashboard(request):
    """Dashboard view for uploading CSV reports and viewing disease predictions"""
    context = {
        'upload_status': None,
        'upload_progress': None,
    }
    
    # Load analysis results history
    recent_analyses = AnalysisResult.objects.filter(user=request.user).order_by('-created_at')[:3]
    context['recent_analyses'] = recent_analyses
    
    if request.method == 'POST':
        try:
            # Get the uploaded file
            csv_file = request.FILES.get('csv_file')
            patient_name = request.POST.get('patient_name', '').strip()
            report_type = request.POST.get('report_type', 'general')
            details = request.POST.get('details', '').strip()
            
            logger.info(f"[CSV_UPLOAD] User {request.user.email} initiated upload. Files: {list(request.FILES.keys())}")
            
            # ============ FILE VALIDATION ============
            if not csv_file:
                context['error'] = 'Please select a CSV file to upload.'
                logger.warning(f"[CSV_UPLOAD] No file provided by {request.user.email}")
                return render(request, 'dashboard.html', context)
            
            logger.info(f"[CSV_UPLOAD] File received: {csv_file.name} ({csv_file.size} bytes)")
            
            # Validate file extension
            if not csv_file.name.lower().endswith('.csv'):
                context['error'] = 'Invalid file format. Please upload a CSV file.'
                logger.warning(f"[CSV_UPLOAD] Invalid file type: {csv_file.name}")
                return render(request, 'dashboard.html', context)
            
            # Validate file size (10MB limit)
            max_size = 10 * 1024 * 1024
            if csv_file.size > max_size:
                context['error'] = f'File size exceeds 10MB limit. Your file is {csv_file.size / 1024 / 1024:.2f}MB.'
                logger.warning(f"[CSV_UPLOAD] File too large: {csv_file.size} bytes")
                return render(request, 'dashboard.html', context)
            
            # ============ CSV PARSING ============
            try:
                logger.info(f"[CSV_UPLOAD] Parsing CSV file...")
                csv_file.seek(0)  # Reset file pointer
                decoded_file = csv_file.read().decode('utf-8').splitlines()
                csv_reader = csv.DictReader(decoded_file)
                medical_data = list(csv_reader)
                
                if not medical_data:
                    context['error'] = 'CSV file is empty. Please provide at least one medical record.'
                    logger.warning(f"[CSV_UPLOAD] Empty CSV file uploaded by {request.user.email}")
                    return render(request, 'dashboard.html', context)
                
                # Validate required columns
                required_columns = {'age', 'gender', 'blood_pressure', 'cholesterol', 'glucose'}
                csv_columns = set(medical_data[0].keys()) if medical_data else set()
                missing_columns = required_columns - csv_columns
                
                if missing_columns:
                    context['error'] = f'CSV missing required columns: {", ".join(sorted(missing_columns))}'
                    logger.warning(f"[CSV_UPLOAD] Missing columns: {missing_columns}")
                    return render(request, 'dashboard.html', context)
                
                logger.info(f"[CSV_UPLOAD] ✓ Successfully parsed {len(medical_data)} records")
                logger.info(f"[CSV_UPLOAD] CSV columns: {list(medical_data[0].keys())}")
                
            except UnicodeDecodeError:
                context['error'] = 'CSV file encoding error. Please use UTF-8 encoding.'
                logger.error(f"[CSV_UPLOAD] Unicode decode error: {csv_file.name}")
                return render(request, 'dashboard.html', context)
            except Exception as e:
                context['error'] = f'Error parsing CSV file: {str(e)}'
                logger.error(f"[CSV_UPLOAD] CSV parsing failed: {str(e)}", exc_info=True)
                return render(request, 'dashboard.html', context)
            
            # ============ DATABASE STORAGE ============
            try:
                logger.info(f"[CSV_UPLOAD] Creating MedicalReport...")
                # Reset file pointer before saving
                csv_file.seek(0)
                
                # Generate default patient name if not provided
                if not patient_name:
                    patient_name = f'Patient {datetime.now().strftime("%Y%m%d%H%M%S")}'
                
                medical_report = MedicalReport.objects.create(
                    user=request.user,
                    patient_name=patient_name,
                    details=details,
                    csv_file=csv_file
                )
                logger.info(f"[CSV_UPLOAD] ✓ Medical report created with ID: {medical_report.id}")
                
            except Exception as e:
                context['error'] = f'Error saving medical report: {str(e)}'
                logger.error(f"[CSV_UPLOAD] Failed to save MedicalReport: {str(e)}", exc_info=True)
                return render(request, 'dashboard.html', context)
            
            # ============ DISEASE PREDICTION ============
            try:
                logger.info(f"[CSV_UPLOAD] Starting disease prediction for {len(medical_data)} records...")
                prediction_results = predict_from_csv(medical_data)
                logger.info(f"[CSV_UPLOAD] ✓ Prediction complete. Total diseases analyzed: {prediction_results['total_diseases']}")
                
            except Exception as e:
                context['error'] = f'Error during disease prediction: {str(e)}'
                logger.error(f"[CSV_UPLOAD] Disease prediction failed: {str(e)}", exc_info=True)
                return render(request, 'dashboard.html', context)
            
            # ============ RESULT FORMATTING & STORAGE ============
            try:
                # Format top 15 predictions
                formatted_predictions = prediction_results['predictions'][:15]
                disease_names = [str(p['disease']) for p in formatted_predictions]
                disease_confidences = [float(p['confidence']) for p in formatted_predictions]
                
                logger.info(f"[CSV_UPLOAD] Saving analysis results to database...")
                analysis_result = AnalysisResult.objects.create(
                    medical_report=medical_report,
                    user=request.user,
                    total_patients=len(medical_data),
                    total_diseases_analyzed=prediction_results['total_diseases'],
                    high_risk_count=prediction_results['high_risk_count'],
                    medium_risk_count=prediction_results['medium_risk_count'],
                    low_risk_count=prediction_results['low_risk_count'],
                    average_confidence=prediction_results['avg_confidence'],
                    predictions_json=prediction_results
                )
                logger.info(f"[CSV_UPLOAD] ✓ Analysis result saved with ID: {analysis_result.id}")
                
                # Prepare context for template
                context['results'] = {
                    'analysis_id': analysis_result.id,
                    'predictions': [(str(p['disease']), int(p['confidence']), str(p['risk'])) for p in formatted_predictions],
                    'disease_names': json.dumps(disease_names),
                    'disease_confidences': json.dumps(disease_confidences),
                    'total_diseases': prediction_results['total_diseases'],
                    'high_risk_count': prediction_results['high_risk_count'],
                    'medium_risk_count': prediction_results['medium_risk_count'],
                    'low_risk_count': prediction_results['low_risk_count'],
                    'avg_confidence': prediction_results['avg_confidence'],
                    'full_predictions': formatted_predictions,
                }
                
                context['success'] = f'✓ Successfully analyzed {len(medical_data)} patient records!'
                logger.info(f"[CSV_UPLOAD] ✓✓✓ UPLOAD COMPLETE by {request.user.email}")
                
            except Exception as e:
                context['error'] = f'Error saving analysis results: {str(e)}'
                logger.error(f"[CSV_UPLOAD] Failed to save AnalysisResult: {str(e)}", exc_info=True)
                return render(request, 'dashboard.html', context)
        
        except Exception as e:
            context['error'] = f'An unexpected error occurred: {str(e)}'
            logger.error(f"[CSV_UPLOAD] Unexpected error: {str(e)}", exc_info=True)
    
    return render(request, 'dashboard.html', context)


@login_required(login_url='login')
def analysis_detail(request, analysis_id):
    """View detailed analysis results"""
    try:
        analysis = AnalysisResult.objects.get(id=analysis_id, user=request.user)
        
        predictions = analysis.get_top_predictions(limit=15)
        disease_names = [p['disease'] for p in predictions]
        disease_confidences = [p['confidence'] for p in predictions]
        
        context = {
            'analysis': analysis,
            'results': {
                'analysis_id': analysis.id,
                'predictions': [(p['disease'], p['confidence'], p['risk']) for p in predictions],
                'disease_names': disease_names,
                'disease_confidences': disease_confidences,
                'total_diseases': analysis.total_diseases_analyzed,
                'high_risk_count': analysis.high_risk_count,
                'medium_risk_count': analysis.medium_risk_count,
                'low_risk_count': analysis.low_risk_count,
                'avg_confidence': analysis.average_confidence,
                'full_predictions': predictions,
            },
            'report': analysis.medical_report,
        }
        
        return render(request, 'analysis_detail.html', context)
        
    except AnalysisResult.DoesNotExist:
        return redirect('dashboard')


@login_required(login_url='login')
def analysis_history(request):
    """View all analysis history with pagination and search"""
    analyses = AnalysisResult.objects.filter(user=request.user).order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    from_date = request.GET.get('from_date', '')
    to_date = request.GET.get('to_date', '')
    
    if search_query:
        analyses = analyses.filter(
            Q(medical_report__patient_name__icontains=search_query) |
            Q(medical_report__csv_file__icontains=search_query)
        )
    
    if from_date:
        try:
            from_datetime = datetime.strptime(from_date, '%Y-%m-%d')
            analyses = analyses.filter(created_at__gte=from_datetime)
        except ValueError:
            pass
    
    if to_date:
        try:
            to_datetime = datetime.strptime(to_date, '%Y-%m-%d')
            to_datetime = to_datetime.replace(hour=23, minute=59, second=59)
            analyses = analyses.filter(created_at__lte=to_datetime)
        except ValueError:
            pass
    
    # Calculate statistics
    total_analyses = analyses.count()
    avg_conf = analyses.aggregate(django_models.Avg('average_confidence'))['average_confidence__avg']
    total_patients = sum(a.total_patients for a in analyses) if analyses.exists() else 0
    
    # Pagination
    paginator = Paginator(analyses, 10)  # 10 analyses per page
    page = request.GET.get('page')
    
    try:
        analyses_page = paginator.page(page)
    except PageNotAnInteger:
        analyses_page = paginator.page(1)
    except EmptyPage:
        analyses_page = paginator.page(paginator.num_pages)
    
    # Add helper methods to analyses for template
    for analysis in analyses_page:
        # Parse predictions from JSON
        try:
            predictions = analysis.predictions_json if isinstance(analysis.predictions_json, list) else []
            analysis.get_high_risk_count = sum(1 for p in predictions if p.get('risk') == 'High')
            analysis.get_medium_risk_count = sum(1 for p in predictions if p.get('risk') == 'Medium')
            analysis.get_low_risk_count = sum(1 for p in predictions if p.get('risk') == 'Low')
        except:
            analysis.get_high_risk_count = 0
            analysis.get_medium_risk_count = 0
            analysis.get_low_risk_count = 0
    
    context = {
        'analyses': analyses_page,
        'page_obj': analyses_page,
        'is_paginated': paginator.num_pages > 1,
        'total_analyses': total_analyses,
        'avg_confidence': round(avg_conf, 2) if avg_conf else 0,
        'total_patients': total_patients,
        'search': search_query,
        'from_date': from_date,
        'to_date': to_date,
    }
    
    return render(request, 'analysis_history.html', context)


@login_required(login_url='login')
def delete_analysis(request, analysis_id):
    """Delete an analysis result"""
    try:
        analysis = AnalysisResult.objects.get(id=analysis_id, user=request.user)
        analysis.medical_report.delete()  # This will cascade delete the analysis
        logger.info(f"Analysis {analysis_id} deleted by {request.user.email}")
        return redirect('dashboard')
    except AnalysisResult.DoesNotExist:
        return redirect('dashboard')