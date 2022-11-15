from django.shortcuts import HttpResponse, render
from django.template import loader
from .models import Course, Schedule, Course_Schedule, Prereq

def index(request):
    if not request.user.is_authenticated:
        # TODO: load the template with no prepopulated schedule info
        pass

    schedule = Schedule.objects.filter(user=request.user)
    if not schedule.exists():
        # same as above, I'm pretty sure, since user will also be authenticated on create request
        pass
    else:
        schedule = schedule[0] # order is undefined here; use last_edited eventually
    
    courses = Course.objects.all()
    sched_courses = Course_Schedule.objects.filter(schedule=schedule)
    unsched_courses = courses.exclude(course_number__in=sched_courses.values('course'))
    unsched_req = unsched_courses.filter(required=True)
    unsched_elec = unsched_courses.filter(required=False)

    context = {
        "schedule": schedule,
        "courses": courses,
        "sched_courses": sched_courses,
        "unsched_courses": unsched_courses,
        "unsched_req": unsched_req,
        "unsched_elec": unsched_elec
    }
    return render(request, 'planner/index.html', context)