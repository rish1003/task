
from django.db import models
from django.contrib.auth.hashers import make_password

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
    
  

    def __str__(self):
        return self.username
