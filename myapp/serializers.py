from rest_framework import serializers
from myapp.models import BlogPost, User
from django.contrib.auth.hashers import make_password

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)  
    
    class Meta:
        model = User
        fields = '__all__'

   
class BlogPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPost
        fields = '__all__'
        
    def get_summary(self, obj):
        return obj.truncated_summary()
    
    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None