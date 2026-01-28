from django.shortcuts import render,redirect
from.models import *
import logging
from django.contrib.auth import login,logout,authenticate
import csv
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
    context = {}
    
    # Load analysis results history
    analysis_history = AnalysisResult.objects.filter(user=request.user)
    context['analysis_history'] = analysis_history[:5]  # Last 5 analyses
    
    if request.method == 'POST':
        try:
            # Get the uploaded file
            csv_file = request.FILES.get('csv_file')
            details = request.POST.get('details', '')
            
            logger.info(f"[UPLOAD] User {request.user.email} attempting upload. Files: {list(request.FILES.keys())}")
            
            if not csv_file:
                error_msg = 'Please select a CSV file to upload.'
                logger.warning(f"[UPLOAD ERROR] No file provided for user {request.user.email}")
                context['error'] = error_msg
                return render(request, 'dashboard.html', context)
            
            logger.info(f"[UPLOAD] File received: {csv_file.name} ({csv_file.size} bytes)")
            
            # Validate file
            if not csv_file.name.endswith('.csv'):
                error_msg = 'File must be in CSV format.'
                logger.warning(f"[UPLOAD ERROR] Invalid file type: {csv_file.name}")
                context['error'] = error_msg
                return render(request, 'dashboard.html', context)
            
            # Check file size (10MB limit)
            if csv_file.size > 10 * 1024 * 1024:
                error_msg = 'File size exceeds 10MB limit.'
                logger.warning(f"[UPLOAD ERROR] File too large: {csv_file.size} bytes")
                context['error'] = error_msg
                return render(request, 'dashboard.html', context)
            
            try:
                # Parse CSV file into list of dictionaries
                logger.info(f"[UPLOAD] Parsing CSV file...")
                decoded_file = csv_file.read().decode('utf-8').splitlines()
                csv_reader = csv.DictReader(decoded_file)
                medical_data = list(csv_reader)
                logger.info(f"[UPLOAD] ✓ Parsed {len(medical_data)} records")
                
                if not medical_data:
                    error_msg = 'CSV file is empty. Please provide medical records.'
                    logger.warning(f"[UPLOAD ERROR] Empty CSV file")
                    context['error'] = error_msg
                    return render(request, 'dashboard.html', context)
                
                # Log column headers
                if medical_data:
                    logger.info(f"[UPLOAD] CSV columns: {list(medical_data[0].keys())}")
                    logger.info(f"[UPLOAD] First record: {medical_data[0]}")
                
            except Exception as e:
                error_msg = f'Error parsing CSV: {str(e)}'
                logger.error(f"[UPLOAD ERROR] CSV parsing failed: {str(e)}", exc_info=True)
                context['error'] = error_msg
                return render(request, 'dashboard.html', context)
            
            logger.info(f"[UPLOAD] Processing {len(medical_data)} medical records for user {request.user.email}")
            
            try:
                # Save medical report to database
                logger.info(f"[UPLOAD] Creating MedicalReport...")
                medical_report = MedicalReport.objects.create(
                    user=request.user,
                    patient_name=request.POST.get('patient_name', f'Patient {datetime.now().strftime("%Y%m%d%H%M%S")}'),
                    details=details
                )
                
                # Save the uploaded CSV file
                medical_report.csv_file = csv_file
                medical_report.save()
                logger.info(f"[UPLOAD] ✓ Medical report saved with ID: {medical_report.id}")
                
            except Exception as e:
                error_msg = f'Error saving report: {str(e)}'
                logger.error(f"[UPLOAD ERROR] Failed to save MedicalReport: {str(e)}", exc_info=True)
                context['error'] = error_msg
                return render(request, 'dashboard.html', context)
            
            try:
                # Use rule-based disease prediction
                logger.info(f"[UPLOAD] Starting disease prediction...")
                prediction_results = predict_from_csv(medical_data)
                logger.info(f"[UPLOAD] ✓ Prediction complete: {prediction_results['total_diseases']} diseases")
                
            except Exception as e:
                error_msg = f'Error in prediction: {str(e)}'
                logger.error(f"[UPLOAD ERROR] Disease prediction failed: {str(e)}", exc_info=True)
                context['error'] = error_msg
                return render(request, 'dashboard.html', context)
            
            try:
                # Format results for template
                formatted_predictions = prediction_results['predictions'][:15]  # Top 15 diseases
                disease_names = [p['disease'] for p in formatted_predictions]
                disease_confidences = [p['confidence'] for p in formatted_predictions]
                
                # Save analysis results to database
                logger.info(f"[UPLOAD] Creating AnalysisResult...")
                analysis_result = AnalysisResult.objects.create(
                    medical_report=medical_report,
                    user=request.user,
                    total_patients=len(medical_data),
                    total_diseases_analyzed=prediction_results['total_diseases'],
                    high_risk_count=prediction_results['high_risk_count'],
                    medium_risk_count=prediction_results['medium_risk_count'],
                    low_risk_count=prediction_results['low_risk_count'],
                    average_confidence=prediction_results['avg_confidence'],
                    predictions_json=prediction_results  # Store entire results as JSON
                )
                logger.info(f"[UPLOAD] ✓ Analysis result saved with ID: {analysis_result.id}")
                
                context['results'] = {
                    'analysis_id': analysis_result.id,
                    'predictions': [(p['disease'], p['confidence'], p['risk']) for p in formatted_predictions],
                    'disease_names': disease_names,
                    'disease_confidences': disease_confidences,
                    'total_diseases': prediction_results['total_diseases'],
                    'high_risk_count': prediction_results['high_risk_count'],
                    'medium_risk_count': prediction_results['medium_risk_count'],
                    'low_risk_count': prediction_results['low_risk_count'],
                    'avg_confidence': prediction_results['avg_confidence'],
                    'full_predictions': formatted_predictions,
                }
                
                success_msg = f'Successfully analyzed {len(medical_data)} patient records using AI models!'
                context['success'] = success_msg
                logger.info(f"[UPLOAD] ✓✓✓ SUCCESS: CSV uploaded and analyzed by {request.user.email}")
                
            except Exception as e:
                error_msg = f'Error saving results: {str(e)}'
                logger.error(f"[UPLOAD ERROR] Failed to save AnalysisResult: {str(e)}", exc_info=True)
                context['error'] = error_msg
                return render(request, 'dashboard.html', context)
            
        except Exception as e:
            error_msg = f'Error processing file: {str(e)}'
            context['error'] = error_msg
            logger.error(f"[UPLOAD ERROR] Unexpected error: {str(e)}", exc_info=True)

    
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