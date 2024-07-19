"""
URL configuration for assign project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
from django.urls import include, path
from myapp import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),  
    path('signup/patient/', views.patient_signup_page, name='patient_signup_page'), 
    path('signup/patient/signup/', views.patient_signup, name='patient_signup'), 
    path('signup/doctor/', views.doctor_signup_page, name='doctor_signup_page'),  
    path('signup/doctor/signup/', views.doctor_signup, name='doctor_signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('createbp/',views.create_blog_post,name='create_blog_post'),
    path('displaydocdash/',views.display_doctor_dashboard, name="display_doctor_dashboard"),
    path('displaypatdash/',views.display_patient_dashboard, name="display_patient_dashboard"),
    path('blog/<int:blog_post_id>/', views.view_blog_post, name='view_blog_post'),
    path('blog/<int:blog_post_id>/delete/', views.delete_blog_post, name='delete_blog_post'),
    path('book_appointment/<int:doctor_id>/', views.book_appointment, name='book_appointment'),
    path('v1/calendar/init/', views.google_calendar_init_view, name='google_permission'),
    path('v1/calendar/redirect/', views.google_calendar_redirect_view, name='google_redirect')
   
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
                      )