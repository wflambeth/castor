from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.postgres.fields import ArrayField

# Inherits from Django's default user model; defining custom
# user model allows for extensibility in the future
class User(AbstractUser):
    # username - required, 150 chars or fewer
    # first_name - optional, 150 chars or fewer
    # last_name - optional, 150 chars or fewer
    # email - optional
    # is_staff - boolean, designates admin site access
    # is_active - boolean, set False to remove account 
    # last_login - datetime, auto-updated on login
    # date_joined - datetime, auto-updated on creation
    pass

# Represents an individual course in the catalog. Courses:
# - Have a unique course number (used as primary key)
# - May be worth 1-16 credits
# - May be offered in any combination of quarters
# - May be required or elective
class Course(models.Model):
    course_number = models.PositiveSmallIntegerField(primary_key=True)
    title = models.CharField(max_length=100, unique=True)
    credits = models.PositiveSmallIntegerField(
        default=4,
        validators=[MaxValueValidator(16), MinValueValidator(1)]
    )
    qtrs = ArrayField(models.PositiveSmallIntegerField(), size=4)
    required = models.BooleanField(default=False)

    class Meta:
        ordering = ['course_number']

    def __str__(self):
        return "CS " + str(self.course_number) + " - " + str(self.title)

# Represents a schedule created by a user. Schedules:
# - Are associated with a given User (foreign key)
# - Have defined start and end quarters, and include all quarters between
class Schedule(models.Model):
    class Quarter(models.IntegerChoices):
        WINTER = 0
        SPRING = 1
        SUMMER = 2
        FALL = 3

    user = models.ForeignKey('User', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default="My new schedule")
    start_qtr = models.PositiveSmallIntegerField(choices=Quarter.choices)
    end_qtr = models.PositiveSmallIntegerField(choices=Quarter.choices)
    start_year = models.PositiveSmallIntegerField() 
    end_year = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ['id']

    # TODO: add check constraint for start < end

    def __str__(self):
        return str(self.id) + ' - ' + self.name

# Intersection table capturing M:M relationship between Courses and Schedules.
# Each Course_Schedule also cpatures the year and quarter the course is slotted into
class Course_Schedule(models.Model):
    schedule = models.ForeignKey('Schedule', on_delete=models.CASCADE)
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    year = models.PositiveSmallIntegerField()
    qtr = models.PositiveSmallIntegerField(choices=Schedule.Quarter.choices)

    constraints = [
        models.UniqueConstraint(fields=['schedule', 'course'], 
                                name='unique_class_instance_per_schedule')
        # TODO: add check constraint for year/qtr within schedule bounds
    ]

    def __str__(self):
        return str(self.schedule) + " - " + str(self.course.course_number) + \
                " (" + str(self.qtr) + " " + str(self.year) + ")"

# Table capturing M:M relationship between Courses and their prerequisite Courses
class Prereq(models.Model):
    course = models.ForeignKey('Course', related_name='course', on_delete=models.CASCADE)
    prereq = models.ForeignKey('Course', related_name='prereq', on_delete=models.CASCADE)

    def __str__(self):
        return "CS " + str(self.course.course_number) + \
               " :: CS " + str(self.prereq.course_number)