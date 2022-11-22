import json
from django.shortcuts import HttpResponse, render
from django.template import loader
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseBadRequest
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

    sched_terms = {}
    qtr = schedule.start_qtr
    year = schedule.start_year
    qtr_set = []
    while year <= schedule.end_year:
        if year == schedule.end_year and qtr > schedule.end_qtr:
            break
        
        this_qtr = (year, qtr)
        sched_terms[this_qtr] = []
        qtr_courses = sched_courses.filter(year=year,qtr=qtr)
        for course in qtr_courses:
            sched_terms[this_qtr].append(course)

        qtr = qtr + 1 if qtr < 3 else 0
        if qtr == 0:
            year += 1

    context = {
        "schedule": schedule,
        "sched_terms": sched_terms,
        "unsched_req": unsched_req,
        "unsched_elec": unsched_elec
    }
    return render(request, 'planner/index.html', context)

def save(request):
    if not request.user.is_authenticated:
        return HttpResponseForbidden('Not logged in')
    data = json.loads(request.body)
    schedule = Schedule.objects.filter(user=request.user).get(id=int(data['s']))
    
    if not schedule:
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
            crs_sch = crs_sch[0]
        
        crs_sch.year = term['year']
        crs_sch.qtr = term['qtr']
        crs_sch.save()

    return JsonResponse({'status': 'saved', 'schedule': schedule.id}, status=200)
    