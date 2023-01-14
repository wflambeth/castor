import json
import planner.utils.schedloader as sl
import planner.utils.schedupdater as su
from django.shortcuts import HttpResponse, render, redirect
from django.template import loader
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_safe
from planner.models import Course, Schedule, Course_Schedule, Prereq

@require_safe
def index(request):
    # If user is logged out, show 'demo' schedule
    if not request.user.is_authenticated:
        return render(request, 'planner/index.html', sl.demo())

    sched_list = Schedule.objects.filter(user=request.user)
    # If user is logged in and has no schedules, create one
    if not sched_list.exists() and len(sched_list) < 10:
        return redirect('/create')
  
    # If user requests existing schedule, return it
    id = request.GET.get('id')
    if id:
        try: 
            schedule = sched_list.get(id=id)
        except Schedule.DoesNotExist:
            schedule = sched_list[0]
    # If user did not request a specific schedule (or requested
    # an invalid one), return oldest schedule
    else:
        schedule = sched_list[0]
    
    context = sl.existing(schedule)
    context['user'] = request.user
    context['sched_list'] = sched_list
    return render(request, 'planner/index.html', context)

@login_required
@require_http_methods(["GET"])
def create(request):
    sched_list = Schedule.objects.filter(user=request.user)
    # TODO: error messaging around the number of schedules one can create
    if len(sched_list) > 9:
        return redirect('/')
    
    schedule = sl.new(request.user)
    schedule.save()
    return redirect(f'/?id={schedule.id}')

@login_required
@require_http_methods(["POST"])
def save(request): 
    data = json.loads(request.body)
    try:
        schedule = Schedule.objects.filter(user=request.user).get(id=int(data['s']))
    except Schedule.DoesNotExist:
        return HttpResponseBadRequest('Schedule not found')
    
    su.update(schedule, data['courses'])
    return JsonResponse({'status': 'saved', 'schedule': schedule.id}, status=200)

@login_required
@require_http_methods(["DELETE"])
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
    
    