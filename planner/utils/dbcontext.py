
from planner.models import Course, Schedule, Course_Schedule, Prereq
from datetime import datetime

def no_auth():
    """
    If user is not logged in, create an empty schedule with 4 terms covering the current year. 
    """
    year = datetime.now().year
    context = {
        "unsched_req": Course.objects.filter(required=True),
        "unsched_elec": Course.objects.filter(required=False),
        "sched_qtrs": {
            (year,0): [],
            (year,1): [], 
            (year,2): [],
            (year,3): []
        }
    }

    return context

def schedule(schedule):
    # TODO: find a way to order these (last edited would be good; needs a model update. maybe most recently created?)
    # Currently, this will always display only the first schedule
    schedule = schedule[0]

    sched_courses = Course_Schedule.objects.filter(schedule=schedule)
    unsched_courses = Course.objects.all().exclude(course_number__in=sched_courses.values('course'))

    sched_qtrs = {}
    
    qtr = schedule.start_qtr
    year = schedule.start_year
    while year <= schedule.end_year:
        if year == schedule.end_year and qtr > schedule.end_qtr:
            break

        sched_qtrs[(year, qtr)] = []
        for course in sched_courses.filter(year=year, qtr=qtr):
            sched_qtrs[(year, qtr)].append(course)
        
        qtr = qtr + 1 if qtr < 3 else 0 
        if qtr == 0: 
            year += 1
    
    context = {
        "schedule": schedule,
        "unsched_req": unsched_courses.filter(required=True),
        "unsched_elec": unsched_courses.filter(required=False),
        "sched_qtrs": sched_qtrs
    }

    return context





