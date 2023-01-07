import json
import planner.utils.dbcontext as dbc
from django.shortcuts import HttpResponse, render
from django.template import loader
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from planner.models import Course, Schedule, Course_Schedule, Prereq

def index(request):
    if not request.user.is_authenticated:
        return render(request, 'planner/index.html', dbc.no_auth())

    schedule = Schedule.objects.filter(user=request.user)
    if not schedule.exists():
        # TODO: separate view branch for users who have no schedules but are logged in
        pass
    else:
        schedule = schedule[0] #TODO: order these schedules somehow (last edited would be good - needs a model update)
    
    courses = Course.objects.all()
    sched_courses = Course_Schedule.objects.filter(schedule=schedule)
    unsched_courses = courses.exclude(course_number__in=sched_courses.values('course'))
    unsched_req = unsched_courses.filter(required=True)
    unsched_elec = unsched_courses.filter(required=False)

    # create year/qtr list to iterate over
    # TODO: break into separate function

    sched_qtrs = {}
    qtr = schedule.start_qtr
    year = schedule.start_year
    while year <= schedule.end_year:
        if year == schedule.end_year and qtr > schedule.end_qtr:
            break
        
        this_qtr = (year, qtr)
        sched_qtrs[this_qtr] = []
        qtr_courses = sched_courses.filter(year=year,qtr=qtr)
        for course in qtr_courses:
            sched_qtrs[this_qtr].append(course)

        qtr = qtr + 1 if qtr < 3 else 0
        if qtr == 0:
            year += 1

    context = {
        "user": request.user,
        "schedule": schedule,
        "unsched_req": unsched_req,
        "unsched_elec": unsched_elec,
        "sched_qtrs": sched_qtrs
    }
    return render(request, 'planner/index.html', context)

def save(request):
    if not request.user.is_authenticated:
        return HttpResponseForbidden('Not logged in')
    data = json.loads(request.body)
    schedule = Schedule.objects.filter(user=request.user).get(id=int(data['s']))
    
    if not schedule: # TODO: .get() above will throw an exception, so this won't ever fire
        return HttpResponseBadRequest('Schedule not found')
    
    for crs_id, term in data['courses'].items():
        print('crs_id:' + crs_id)
        course = Course.objects.get(course_number=int(crs_id))
        print('course:' + str(course))
        print('schedule:' + str(schedule))
        crs_sch = Course_Schedule.objects.filter(schedule=schedule).filter(course=course)
        
        # removing items from current schedule
        if not term['year'] or term['year'] == 'null':
            if crs_sch.exists():
                crs_sch.delete()
                continue
        
        # instantiating our QuerySet if info is to be saved
        if not crs_sch.exists():
            crs_sch = Course_Schedule(course=course, schedule=schedule)
        else:
            crs_sch = crs_sch[0] # TODO: kinda messy to be using same name for this and the other
        
        crs_sch.year = term['year']
        crs_sch.qtr = term['qtr']
        crs_sch.save()

    return JsonResponse({'status': 'saved', 'schedule': schedule.id}, status=200)
    