import datetime

from django.db import models
from django.utils import timezone

class User(models.Model):
    email = models.CharField(max_length=200)
    signup_date = models.DateTimeField('signup date')

    def __str__(self):
        return self.email

    def signed_up_recently(self):
        return self.signup_date >= timezone.now() - datetime.timedelta(days=1)

"""
class Course(models.Model):
    pass

class Schedule(models.Model):
    pass

class Class_to_Schedule(models.Model):
    pass

class Prereq(models.Model):
    pass
"""