from rest_framework import serializers
from myapp.models import User
from django.contrib.auth.hashers import make_password

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)  
    
    class Meta:
        model = User
        fields = ['id', 'fname', 'lname', 'username', 'email', 'password', 'address_line1', 'city', 'state', 'pincode', 'profile_picture', 'user_type']

   
