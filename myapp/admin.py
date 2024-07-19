from django.contrib import admin

from .models import User, BlogPost, Appointment

admin.site.register(User)
admin.site.register(BlogPost)
admin.site.register(Appointment)
