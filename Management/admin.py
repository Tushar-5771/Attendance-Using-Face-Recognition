from django.contrib import admin
from .models import User,Faculty,Attendance

# Register your models here.
admin.site.register(User)
admin.site.register(Faculty)
admin.site.register(Attendance)