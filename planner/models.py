from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.postgres.fields import ArrayField


class User(AbstractUser):
    """Represents registered users of the app.
    
    Inherits from base Django User class, including:
        username
        (hashed) password
        permissions
        email address (opt.)
        first/last names (opt.)
        date joined
        last login
        
    Declaring here allows extension of the User model in the future.
    """
    pass

class Course(models.Model):
    """Represents an individual course in the catalog.
    """
    # Course number (CS XXX) serves as primary key
    # May be worth refactoring, due to CS 406 (variable credit, repeatable)
    course_number = models.PositiveSmallIntegerField(primary_key=True)
    
    # Official course title 
    title = models.CharField(max_length=100, unique=True)
    
    # Number of credits (nearly all courses are 4, but 1-16 are possible)
    credits = models.PositiveSmallIntegerField(
        default=4,
        validators=[MaxValueValidator(16), MinValueValidator(1)]
    )
    # Quarter(s) in which course is offered 
    qtrs = ArrayField(models.PositiveSmallIntegerField(), size=4)
    
    # Whether course is required or elective for CS majors
    required = models.BooleanField(default=False)

    class Meta:
        ordering = ['course_number']

    def __str__(self):
        return "CS " + str(self.course_number) + " - " + str(self.title)

class Schedule(models.Model):
    """ Represents a schedule created by a user.

        Schedules have customizable names and start/end dates.
        Users are stored as foreign keys. 
        Courses link to Schedules via the Course_Schedule intersection table, below.
    """
    # IntegerChoices creates an enum-like class, restricting
    # choices for start_qtr/end_qtr to valid values.
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

class Course_Schedule(models.Model):
    """ Represents a course's assignment to a given schedule.

        Uniqueness enforced on the combination of two foreign keys, 
        Schedule and Course. Also stores year/qtr within schedule.    
    """
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


class Prereq(models.Model):
    """ Represents a prerequisite relationship between two Courses.

        'course' is the course that has a prerequisite, while
        'prereq' is the prerequisite. 

    """
    course = models.ForeignKey(
        'Course', related_name='course', on_delete=models.CASCADE)
    prereq = models.ForeignKey(
        'Course', related_name='prereq', on_delete=models.CASCADE)

        # TODO: Add uniqueness constraint on course/prereq pair

    def __str__(self):
        return "CS " + str(self.course.course_number) + \
               " :: CS " + str(self.prereq.course_number)
