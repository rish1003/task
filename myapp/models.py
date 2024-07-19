
from django.db import models
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError

class User(models.Model):
    
    USER_TYPES = (
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
    )
    fname = models.CharField(max_length=200)
    lname = models.CharField(max_length=200)
    username = models.CharField(max_length = 20,unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    address_line1 = models.CharField(max_length=200)
    city = models.CharField(max_length=30)
    state = models.CharField(max_length=20)
    pincode = models.IntegerField()
    user_type = models.CharField(max_length=8, choices=USER_TYPES)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    speciality = models.CharField(max_length=200,null=True,blank=True)
    
  

    def __str__(self):
        return self.username

class BlogPost(models.Model):
    CATEGORY_CHOICES = [
        ('mental_health', 'Mental Health'),
        ('heart_disease', 'Heart Disease'),
        ('covid19', 'Covid19'),
        ('immunization', 'Immunization'),
    ]
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    summary = models.TextField()
    content = models.TextField()
    is_draft = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def truncated_summary(self):
        words = self.summary.split()
        if len(words) > 15:
            return ' '.join(words[:15]) + '...'
        else:
            return self.summarys
    def __str__(self):
        return self.title
    
    
class Appointment(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE,related_name="patient")
    doctor = models.ForeignKey(User, on_delete=models.CASCADE,related_name="doctor")
    time = models.DateTimeField(null=False)
    speciality = models.CharField(max_length=200,null=False)
    
    def save(self, *args, **kwargs):
        if self.patient.user_type != 'patient':
            raise ValidationError(f"User {self.patient.username} is not a patient.")
        if self.doctor.user_type != 'doctor':
            raise ValidationError(f"User {self.doctor.username} is not a doctor.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Appointment with Dr. {self.doctor.username} for {self.patient.username} at {self.time}"