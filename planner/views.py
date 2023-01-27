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
    """
    Takes requests to index URL ("/"), and returns a scheduler page. 
    Generally called by links within the template, and includes an "id" URL parameter (optional).
    """

    # If user is logged out, show 'demo' schedule
    if not request.user.is_authenticated:
        return render(request, 'planner/index.html', sl.demo())

    # Check for existing schedules for this user
    # If none exist, create one and return to this flow
    sched_list = Schedule.objects.filter(user=request.user)
    if not sched_list.exists() and len(sched_list) < 10:
        return redirect('/create')
  
    # Get ID of requested schedule
    # (For newly-created schedules, this will be passed by /create handler)
    id = request.GET.get('id')
    if id:
        # attempt to pull requested schedule using ID/user combo
        try: 
            schedule = sched_list.get(id=id)
        except Schedule.DoesNotExist:
            schedule = sched_list[0]
    # If user did not request a specific schedule 
    # (or requested an invalid one), return oldest schedule
    else:
        schedule = sched_list[0]
    
    # Load context, adding the user object and list of user's existing schedules
    # (Avoids passing user object to schedloader. Why do I care about that? Great question.) 
    context = sl.existing(schedule)
    context['user'] = request.user
    context['sched_list'] = sched_list
    # Render template with given context
    return render(request, 'planner/index.html', context)

@login_required
@require_http_methods(["GET"])
def create(request):
    """
    Builds new schedule, and redirects requestor to that schedule's index page. 
    """
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
    """
    Saves updates to schedule (dates, courses scheduled).
    Used by fetch requests within the index page JavaScript. 
    """
    data = json.loads(request.body)
    try:
        schedule = Schedule.objects.filter(user=request.user).get(id=int(data['s']))
    except Schedule.DoesNotExist:
        return HttpResponseBadRequest('Schedule not found')
    
    su.update(schedule, data['courses'], data['dates'])
    return JsonResponse({'status': 'saved', 'schedule': schedule.id}, status=200)

@login_required
@require_http_methods(["GET", "DELETE"])
def delete(request):
    """
    Deletes the schedule with the passed ID, provided
    it exists and is owned by the requesting user. 
    """

    id = request.GET.get('id')
    if not id:
        return HttpResponseBadRequest('No schedule ID provided')
    
    try: 
        schedule = Schedule.objects.filter(user=request.user).get(id=id)
    except Schedule.DoesNotExist:
        return HttpResponseBadRequest('Schedule not found')
    
    schedule.delete()
    
    # Handles requests to delete the schedule a user is currently viewing
    if request.method == 'GET':
        return redirect('/')
    else:
        # For async fetch requests from within the page
        return HttpResponse(status=204)

@login_required
@require_http_methods(["POST"])
def update_title(request):
    """
    Updates the title of a given schedule. 
    TODO: Curently disabled, due to jankiness of implementation. Watch this space!
    """
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
    
    