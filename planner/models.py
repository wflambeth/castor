from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator

class User(AbstractUser):
    pass

class Course(models.Model):
    # using non-serial PK for this, we'll see how it goes
    course_number = models.PositiveSmallIntegerField(primary_key=True)
    title = models.CharField(max_length=100, unique=True)
    credits = models.PositiveSmallIntegerField(
        default=4,
        validators=[MaxValueValidator(16), MinValueValidator(1)]
    )
    required = models.BooleanField()

class Schedule(models.Model):
    class Quarter(models.IntegerChoices):
        WINTER = 0
        SPRING = 1
        SUMMER = 2
        FALL = 3

    user = models.ForeignKey('User', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default=f"{user.name}'s Schedule{str(id)}") # not enforcing uniqueness on this for now
    start_qtr = models.PositiveSmallIntegerField(choices=Quarter.choices)
    end_qtr = models.PositiveSmallIntegerField(choices=Quarter.choices)
    start_year = models.PositiveSmallIntegerField() 
    end_year = models.PositiveSmallIntegerField()

    # TODO: add check constraint for start < end

class Course_Schedule(models.Model):
    schedule = models.ForeignKey('Schedule', on_delete=models.CASCADE)
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    year = models.PositiveSmallIntegerField()
    qtr = models.PositiveSmallIntegerField(choices=Schedule.Quarter.choices)

    constraints = [
        models.UniqueConstraint(fields=['schedule', 'course'], name='unique_class_instance_per_schedule')
        # TODO: add check constraint for year/qtr within schedule bounds
    ]

class Prereq(models.Model):
    course = models.ForeignKey('Course', related_name='course', on_delete=models.CASCADE)
    prereq = models.ForeignKey('Course', related_name='prereq', on_delete=models.CASCADE)