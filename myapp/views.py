from datetime import datetime, timedelta
import os
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils import timezone
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from rest_framework.response import Response
import google.oauth2.credentials
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
import os

from rest_framework.decorators import api_view

from googleapiclient.errors import HttpError
from myapp.models import Appointment, BlogPost, User
from myapp.serializers import UserSerializer, BlogPostSerializer
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect

from django.contrib.auth import logout

from django.shortcuts import render, redirect

from assign.settings import *
def get_user_data(user):
    profile_picture_url = user.profile_picture.url if user.profile_picture else None
    specialties = user.speciality.split(',') if user.speciality else []

    user_data = {
        'id' : user.id,
        'first_name': user.fname,
        'last_name': user.lname,
        'username': user.username,
        'email': user.email,
        'address_line1': user.address_line1,
        'city': user.city,
        'state': user.state,
        'pincode': user.pincode,
        'profile_picture_url': profile_picture_url,
        'user_type': user.user_type,
        'specialties': [specialty.strip() for specialty in specialties] if specialties is not None else []
    }
    return user_data



def get_blog_post_data(blog_post):
    image_url = blog_post.image.url if blog_post.image else None
    blog_post_data = {
        'id': blog_post.id,
        'title': blog_post.title,
        'category': blog_post.category,
        'summary': blog_post.summary,
        'content': blog_post.content,
        'author': blog_post.author.username,
        'image_url': image_url,
        'draft': 'yes' if blog_post.is_draft else 'no'
    }
    return blog_post_data


def list_doctors_by_category():
    doctors = User.objects.filter(user_type='doctor')
    categories = {}
    for doctor in doctors:
        if doctor.speciality is not None:
            specialties = doctor.speciality.split(',') 
        else:
            continue
        for specialty in specialties:
            specialty = specialty.strip()
            if specialty not in categories:
                categories[specialty] = []
            categories[specialty].append(get_user_data(doctor))

    return categories

@api_view(['POST'])
@csrf_exempt
def patient_signup(request):
    if request.method == 'POST':
        mutable_data = request.data.copy()
        mutable_data['user_type'] = 'patient'
        serializer = UserSerializer(data=mutable_data)
        if serializer.is_valid():
            user = serializer.save()
            user_data = get_user_data(user) 
            request.session['user_id'] = user.id
            blog_posts = BlogPost.objects.filter(is_draft=False).order_by('category')  
            serialized_blog_posts = [get_blog_post_data(post) for post in blog_posts]
            cat = list_doctors_by_category()
            context = {
                'user': user_data,
                'blog_posts': serialized_blog_posts,
                'categories' : cat
            }
            return render(request, 'patient_dashboard.html', context)
          
        errors = serializer.errors

        data = {
            'fname': request.data.get('fname', ''),
            'lname': request.data.get('lname', ''),
            'username': request.data.get('username', ''),
            'email': request.data.get('email', ''),
            'address_line1': request.data.get('address_line1', ''),
            'city': request.data.get('city', ''),
            'state': request.data.get('state', ''),
            'pincode': request.data.get('pincode', '')
        }
        return render(request, 'patient_signup.html', {'errors': errors, **data})


@api_view(['POST'])
@csrf_exempt
def doctor_signup(request):
    if request.method == 'POST':
        mutable_data = request.data.copy()
        mutable_data['user_type'] = 'doctor'
        serializer = UserSerializer(data=mutable_data)
        if serializer.is_valid():
            user = serializer.save()
            request.session['user_id'] = user.id
            user1 = get_user_data(user)
            blog_posts = BlogPost.objects.filter(author=user).order_by('category')
            serialized_blog_posts = [get_blog_post_data(post) for post in blog_posts]
            context = {
            'user': user1,
            'blog_posts': serialized_blog_posts
             }
            return render(request, 'doctor_dashboard.html', context)
        errors = serializer.errors
     
        data = {
            'fname': request.data.get('fname', ''),
            'lname': request.data.get('lname', ''),
            'username': request.data.get('username', ''),
            'email': request.data.get('email', ''),
            'address_line1': request.data.get('address_line1', ''),
            'city': request.data.get('city', ''),
            'state': request.data.get('state', ''),
            'pincode': request.data.get('pincode', ''),
            'speciality' : request.data.get('specialties','')
        }
        return render(request, 'doctor_signup.html', {'errors': errors, **data})

def home(request):
    return render(request, 'home.html')


def patient_signup_page(request):
    return render(request, 'patient_signup.html')

def doctor_signup_page(request):
    return render(request, 'doctor_signup.html')

@api_view(['POST',"GET"])
@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        username1 = request.POST.get('username')
        password1 = request.POST.get('password')
        
        try:
            user = User.objects.get(username=username1)
        except User.DoesNotExist:
            user = None
     
        if user is not None and (password1==user.password):
            user_data = get_user_data(user)  
            request.session['user_id'] = user.id
            if user.user_type == "doctor":
                blog_posts = BlogPost.objects.filter(author=user).order_by('category')
                serialized_blog_posts = [get_blog_post_data(post) for post in blog_posts]
                appointments = Appointment.objects.filter(doctor=user).order_by("time")
        
                appointment_data = []
                for appointment in appointments:
                    start_time = appointment.time
                    end_time = start_time + timedelta(minutes=45)
                    appointment_data.append({
                        'id': appointment.id,
                        'patient_name': f'{appointment.patient.fname} {appointment.patient.lname}',
                        'date': appointment.time.date(),
                    'stime': appointment.time.time(),
                    'etime': end_time.time(),
                        'specialities' : appointment.speciality
                    })
                print(appointment_data)
                context = {
                    'user': user_data,
                    'blog_posts': serialized_blog_posts,
                    'appointments' : appointment_data
                }
                return render(request, 'doctor_dashboard.html', context)
            else:
                blog_posts = BlogPost.objects.filter(is_draft=False).order_by('category')  
                serialized_blog_posts = [get_blog_post_data(post) for post in blog_posts]
                cat = list_doctors_by_category()
                appts =  get_appointments(request.session.get('user_id'))
                context = {
                'user': user_data,
                'blog_posts': serialized_blog_posts,
                'categories' : cat,
                'appointments': appts
                }
                
                return render(request, 'patient_dashboard.html', context)
         
        else:
            error = 'Invalid username or password. Please try again.'
            return render(request, 'login.html', {'error': error})
    
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('home')




@api_view(['POST','GET'])
@csrf_exempt

def book_appointment(request, doctor_id):
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({'error': 'User not logged in'}, status=400)

        try:
            patient = User.objects.get(id=user_id)
            doctor = User.objects.get(id=doctor_id)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User or Doctor not found'}, status=404)

        appointment_date = request.POST.get('appointment_date')
        appointment_time = request.POST.get('appointment_time')

        if len(appointment_time) == 5:  
            appointment_time += ':00'

        try:
            appointment_datetime = timezone.make_aware(
                datetime.combine(
                    datetime.strptime(appointment_date, '%Y-%m-%d'),
                    datetime.strptime(appointment_time, '%H:%M:%S').time()
                )
            )
        except ValueError as e:
            print(e)
            return JsonResponse({'error': 'Invalid date or time format'}, status=400)

        if Appointment.objects.filter(doctor=doctor, time=appointment_datetime).exists():
            return JsonResponse({'error': 'Appointment slot is already taken'}, status=400)

        next_available_time = appointment_datetime + timedelta(minutes=45)
        if Appointment.objects.filter(doctor=doctor, time__gte=appointment_datetime, time__lt=next_available_time).exists():
            next_slot = next_available_time.strftime('%H:%M:%S')
            return JsonResponse({'error': f'Next available slot is after {next_slot}'}, status=400)

        appointment = Appointment(patient=patient, doctor=doctor, time=appointment_datetime, speciality=request.POST.get("specialty"))
        appointment.save()
        appt_end = appointment_datetime + timedelta(minutes=45)
        
        credentials = request.session.get('credentials')
        if not credentials:
            return JsonResponse({'error': 'User not authenticated'}, status=401)

        try:
            credentials = google.oauth2.credentials.Credentials(**credentials)
            service = googleapiclient.discovery.build(
                API_SERVICE_NAME, API_VERSION, credentials=credentials)

          

            event = {
                'summary': f'Appointment with Dr. {doctor.fname} {doctor.lname}',
                'start': {
                    'dateTime': appointment_datetime.isoformat(),
                    'timeZone': 'Asia/Kolkata',
                },
                'end': {
                    'dateTime': appt_end.isoformat(),
                    'timeZone': 'Asia/Kolkata',
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},
                        {'method': 'popup', 'minutes': 10},
                    ],
                },
                'attendees': [
                    {'email': patient.email},
                    {'email': doctor.email},
                ],
            }

            event_result = service.events().insert(calendarId='primary', body=event).execute()
            event_id = event_result.get('id')
            print(f'Event created: {event_result.get("htmlLink")}')
        
        except HttpError as error:
            return JsonResponse({'error': f'An error occurred: {error}'}, status=500)
        except Exception as e:
            return JsonResponse({'error': f'Failed to create calendar event: {str(e)}'}, status=500)


       
        return JsonResponse({'success': f'Appointment booked successfully\nDoctor: Dr. {doctor.fname} {doctor.lname}\nDate: {appointment_date}\nStart: {appointment_time}\nEnd: {appt_end.time()}'}, status=200)


os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

CLIENT_SECRETS_FILE = "credentials.json"

SCOPES = ['https://www.googleapis.com/auth/calendar',
          'https://www.googleapis.com/auth/userinfo.email',
          'https://www.googleapis.com/auth/userinfo.profile',
          'openid']
REDIRECT_URL = 'http://127.0.0.1:8000/v1/calendar/redirect'
API_SERVICE_NAME = 'calendar'
API_VERSION = 'v3'


@api_view(['GET'])
def google_calendar_init_view(request):
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES)
    flow.redirect_uri = REDIRECT_URL

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true')

    request.session['state'] = state

    return redirect(authorization_url)


@api_view(['GET'])
def google_calendar_redirect_view(request):
    state = request.session.get('state')
    if not state:
        return JsonResponse({"error": "State parameter missing."}, status=400)

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = REDIRECT_URL

    authorization_response = request.get_full_path()
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials
    request.session['credentials'] = credentials_to_dict(credentials)

    credentials = google.oauth2.credentials.Credentials(
        **request.session['credentials'])

    service = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=credentials)

    return JsonResponse({"message": "Google Calendar service initialized"}, status=200)

def credentials_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}
def get_appointments(user_id):

    if not user_id:
        return JsonResponse({'error': 'User not logged in'}, status=400)

    try:
        patient = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)

    appointments = Appointment.objects.filter(patient=patient)

    appointments_with_end_time = []
    for appointment in appointments:
        doctor = User.objects.get(id=appointment.doctor.id)
        end_time = appointment.time + timedelta(minutes=45)

        appointments_with_end_time.append({
            'doctor_name': f"Dr. {appointment.doctor.fname} {appointment.doctor.lname}",
            'date': appointment.time.date(),
            'stime': appointment.time.time(),
            'etime': end_time.time(),
            'specialties': appointment.speciality
        })

    return appointments_with_end_time

@api_view(['POST'])
@csrf_exempt
def create_blog_post(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        author = User.objects.get(id=user_id)
        mutable_data = request.data.copy()
        mutable_data["author"] = author.id
        if 'image' in request.FILES:
            img = request.FILES['image']
            mutable_data["image"] = img  
        serializer = BlogPostSerializer(data=mutable_data)
        if serializer.is_valid():
            bp = serializer.save()
            user_data = get_user_data(author)
            blog_posts = BlogPost.objects.filter(author=author).order_by('category')
            serialized_blog_posts = [get_blog_post_data(post) for post in blog_posts]
            context = {
                'user': user_data,
                'blog_posts': serialized_blog_posts,
                
            }
            return render(request, 'doctor_dashboard.html', context)
        errors = serializer.errors
        data = {
            'title': request.data.get('title', ''),
            'category': request.data.get('category', ''),
            'summary': request.data.get('summary', ''),
            'content': request.data.get('content', ''),
        }
        print(errors)

        return render(request, 'doctor_dashboard.html', {'errors': errors, 'data': data})

def display_doctor_dashboard(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')  

    try:
        user = User.objects.get(id=user_id)
        user_data = get_user_data(user)
        blog_posts = BlogPost.objects.filter(author=user).order_by('category')
        serialized_blog_posts = [get_blog_post_data(post) for post in blog_posts]
        appointments = Appointment.objects.filter(doctor=user).order_by("time")
        
        appointment_data = []
        for appointment in appointments:
            start_time = appointment.time
            end_time = start_time + timedelta(minutes=45)
            appointment_data.append({
                'id': appointment.id,
                'patient_name': f'{appointment.patient.fname} {appointment.patient.lname}',
                'date': appointment.time.date(),
            'stime': appointment.time.time(),
            'etime': end_time.time(),
                'specialities' : appointment.speciality
            })
        
        context = {
            'user': user_data,
            'blog_posts': serialized_blog_posts,
            'appointments' : appointment_data
        }
        return render(request, 'doctor_dashboard.html', context)
    except User.DoesNotExist:
        return redirect('login')  

@csrf_exempt
def display_patient_dashboard(request):
    
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')  

    try:
        user = User.objects.get(id=user_id)
        user_data = get_user_data(user)
        blog_posts = BlogPost.objects.filter(is_draft=False).order_by('category')  
        serialized_blog_posts = [get_blog_post_data(post) for post in blog_posts]
        cat = list_doctors_by_category()
        appts =  get_appointments(request.session.get('user_id'))
        context = {
                'user': user_data,
                'blog_posts': serialized_blog_posts,
                'categories' : cat,
                'appointments': appts
                }
        return render(request, 'patient_dashboard.html', context)
    except User.DoesNotExist:
        return redirect('login')  
    
def view_blog_post(request, blog_post_id):
    blog_post = get_object_or_404(BlogPost, id=blog_post_id)
    context = {
        'blog_post': get_blog_post_data(blog_post)
    }
    return render(request, 'view_blog_post.html', context)


def delete_blog_post(request, blog_post_id):
    if request.method == 'POST':
        blog_post = get_object_or_404(BlogPost, id=blog_post_id)
        blog_post.delete()
    return redirect(display_doctor_dashboard)  

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
