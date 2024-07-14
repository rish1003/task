from django.shortcuts import get_object_or_404, render, redirect
from rest_framework.decorators import api_view
from myapp.models import BlogPost, User
from myapp.serializers import UserSerializer, BlogPostSerializer
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password
from django.contrib.auth import logout


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
            context = {
                'user': user_data,
                'blog_posts': serialized_blog_posts
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
            blog_posts = BlogPost.objects.filter(author=user).order_by('category')
            serialized_blog_posts = [get_blog_post_data(post) for post in blog_posts]
            context = {
            'user': user,
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
            'pincode': request.data.get('pincode', '')
        }
        return render(request, 'doctor_signup.html', {'errors': errors, **data})

def home(request):
    return render(request, 'home.html')


def patient_signup_page(request):
    return render(request, 'patient_signup.html')

def doctor_signup_page(request):
    return render(request, 'doctor_signup.html')

@api_view(['POST',"GET"])
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
                context = {
                 'user': user_data,
                'blog_posts': serialized_blog_posts
                 }
                return render(request, 'doctor_dashboard.html', context)
            else:
                blog_posts = BlogPost.objects.filter(is_draft=False).order_by('category')  
                serialized_blog_posts = [get_blog_post_data(post) for post in blog_posts]
                context = {
                    'user': user_data,
                    'blog_posts': serialized_blog_posts
                }
                return render(request, 'patient_dashboard.html', context)
         
        else:
            error = 'Invalid username or password. Please try again.'
            return render(request, 'login.html', {'error': error})
    
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('home')


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
        context = {
            'user': user_data,
            'blog_posts': serialized_blog_posts
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
        context = {
            'user': user_data,
            'blog_posts': serialized_blog_posts
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