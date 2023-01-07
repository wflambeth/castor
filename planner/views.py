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
    
    if schedule.exists():
        # TODO: neater way of doing this, without passing request object to module
        context = dbc.schedule(schedule)
        context['user'] = request.user
        return render(request, 'planner/index.html', context)
    else:
        # return render(request, 'planner/index.html', TODO some context showing that it's blank)
        pass

def save(request):
    if not request.user.is_authenticated:
        return HttpResponseForbidden('Not logged in')
    
    data = json.loads(request.body)
    try:
        schedule = Schedule.objects.filter(user=request.user).get(id=int(data['s']))
    except Schedule.DoesNotExist:
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
    