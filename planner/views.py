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

    # Altering to retrieve both a specific schedule (to render) and the full list of schedules (for dropdown)
    sched_list = Schedule.objects.filter(user=request.user)
    id = request.GET.get('id', 1)

    try: 
        schedule = sched_list.get(id=id)
    except Schedule.DoesNotExist:
        pass
        # TODO: new user/no schedules, we'll create one for them 

    context = dbc.schedule(schedule)
    context['user'] = request.user
    context['sched_list'] = sched_list
    return render(request, 'planner/index.html', context)


def save(request):
    if not request.user.is_authenticated:
        return HttpResponseForbidden('Not logged in')
    
    data = json.loads(request.body)
    try:
        schedule = Schedule.objects.filter(user=request.user).get(id=int(data['s']))
    except Schedule.DoesNotExist:
        return HttpResponseBadRequest('Schedule not found')
    
    #TODO: pretty messy, could use a refactor
    for crs_id, term in data['courses'].items():
        course = Course.objects.get(course_number=int(crs_id))
        crs_sch = Course_Schedule.objects.filter(schedule=schedule).filter(course=course)
        
        # For courses to be removed from schedule, delete and skip to next loop
        if not term['year'] or term['year'] == 'null':
            if crs_sch.exists():
                crs_sch.delete()
                continue

        # For courses not yet in schedule, create new course_schedule object 
        if not crs_sch.exists():
            crs_sch = Course_Schedule(course=course, schedule=schedule)
        else:
            # For existing course_schedules, need to pull object out of queryset
            crs_sch = crs_sch[0] 
        
        # Update course info and save
        crs_sch.year = term['year']
        crs_sch.qtr = term['qtr']
        crs_sch.save() #TODO: exception handling

    return JsonResponse({'status': 'saved', 'schedule': schedule.id}, status=200)
    