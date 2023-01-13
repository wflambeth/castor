import json
import planner.utils.schedloader as sl
from django.shortcuts import HttpResponse, render, redirect
from django.template import loader
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_safe
from planner.models import Course, Schedule, Course_Schedule, Prereq

@require_safe
def index(request):
    # Option 1: user is logged out; show 'demo' schedule
    if not request.user.is_authenticated:
        return render(request, 'planner/index.html', sl.demo())

    sched_list = Schedule.objects.filter(user=request.user)
    # Option 2: user is logged in and does not have any schedules
    # Option 3: user is requesting to create a new schedule, and is under limit
    if not sched_list.exists() or request.GET.get('create') and len(sched_list) < 10:
        # in either case, create blank schedule and redirect user there
        schedule = sl.new(request.user)
        schedule.save()
        return redirect(f'/?id={schedule.id}')
        
    # Option 4: user is requesting an existing schedule
    id = request.GET.get('id')
    if id:
        try: 
            schedule = sched_list.get(id=id)
        except Schedule.DoesNotExist:
            schedule = sched_list[0]
    else:
        # if no ID passed, return oldest one
        schedule = sched_list[0]
    
    context = sl.existing(schedule)
    context['user'] = request.user
    context['sched_list'] = sched_list
    return render(request, 'planner/index.html', context)

@require_http_methods(["POST"])
def save(request): 
    if not request.user.is_authenticated: #TODO: do I need this? better to just use the decorator?
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

@login_required
def delete(request):
    id = request.GET.get('id')
    if not id:
        return HttpResponseBadRequest('No schedule ID provided')
    
    try: 
        schedule = Schedule.objects.filter(user=request.user).get(id=id)
    except Schedule.DoesNotExist:
        return HttpResponseBadRequest('Schedule not found')
    
    schedule.delete()
    return HttpResponse(status=204)

@login_required
@require_http_methods(["POST"])
def update_title(request):
    data = json.loads(request.body)

    try:
        schedule = Schedule.objects.filter(user=request.user).get(id=int(data['schedule']))
    except Schedule.DoesNotExist:
        return HttpResponseBadRequest('Schedule not found')

    title = data.get('title')
    if title is None:
        return HttpResponseBadRequest('Title not found')
    
    schedule.name = title
    schedule.save()
    
    return JsonResponse({'result': 'Title updated!'}, status=200)
    
    