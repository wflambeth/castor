from django.shortcuts import HttpResponse, render
from django.template import loader
from .models import Course, Schedule, Course_Schedule, Prereq

def index(request):
    if not request.user.is_authenticated:
        # TODO: load the template with no prepopulated schedule info
        # Have a default context that loads when no schedules exist?
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

    # create year/qtr list to iterate over
    # TODO: break into separate function

    sched_info = {}
    qtr = schedule.start_qtr
    year = schedule.start_year
    qtr_set = []
    while year <= schedule.end_year:
        if year == schedule.end_year and qtr > schedule.end_qtr:
            break
        
        this_qtr = (year, qtr)
        sched_info[this_qtr] = []
        qtr_courses = sched_courses.filter(year=year,qtr=qtr)
        for course in qtr_courses:
            sched_info[this_qtr].append(course)

        qtr = qtr + 1 if qtr < 3 else 0
        if qtr == 0:
            year += 1

    context = {
        # To be iterated on/pared down as we go
        "schedule": schedule,
        "courses": courses,
        "sched_courses": sched_courses,
        "unsched_courses": unsched_courses,
        "unsched_req": unsched_req,
        "unsched_elec": unsched_elec,
        "qtr_set": qtr_set,
        "sched_info": sched_info
    }
    return render(request, 'planner/index.html', context)