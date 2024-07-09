from django.shortcuts import render, redirect
from rest_framework.decorators import api_view
from myapp.models import User
from myapp.serializers import UserSerializer
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password


def get_user_data(user):
    profile_picture_url = user.profile_picture.url if user.profile_picture else None
    print(profile_picture_url)
    user_data = {
        
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
    }
    return user_data


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
            print(user_data)
            return render(request, 'dashboard.html', {'user':user_data})
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
            user_data = get_user_data(user)  
            return render(request, 'dashboard.html', {'user':user_data})
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
        return render(request, 'doctor_signup.html', {'errors': errors, **data})

def home(request):
    return render(request, 'home.html')


def patient_signup_page(request):
    return render(request, 'patient_signup.html')

def doctor_signup_page(request):
    return render(request, 'doctor_signup.html')


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
            return render(request, 'dashboard.html', {'user':user_data})
        else:
            error = 'Invalid username or password. Please try again.'
            return render(request, 'login.html', {'error': error})
    
    return render(request, 'login.html')
