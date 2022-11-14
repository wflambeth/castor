from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Course, Schedule, Course_Schedule, Prereq 

admin.site.register(User, UserAdmin)
admin.site.register(Course)
admin.site.register(Schedule)
admin.site.register(Course_Schedule) 
admin.site.register(Prereq)