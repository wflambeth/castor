import json
import planner.utils.schedloader as sl
import planner.utils.schedupdater as su
from django.shortcuts import HttpResponse, render, redirect
from django.http import JsonResponse, HttpResponseBadRequest,\
                        HttpResponseServerError, HttpResponseNotAllowed
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_safe
from planner.models import Schedule
from planner.forms import TitleForm

MAX_SCHEDULES = 10

@require_safe
def index(request):
    """
    Loads a demo page if user is unauthenticated. 
    If user is authenticated, redirects to their most recent schedule.
    """

    # If user is logged out, show 'demo' schedule
    if not request.user.is_authenticated:
        return render(request, 'planner/index.html', sl.demo())

    # Check for existing schedules for this user
    sched_list = Schedule.objects.filter(user=request.user)
    # Load most recently created, if possible...
    if sched_list.exists():
        schedule = sched_list.last()
    # ...or if they have no schedules, create new one
    else:
        try:
            schedule = sl.new(request.user)
            schedule.save()
        except Exception as e:
            print(e) # TODO: turn this into a logging statement
            return HttpResponseServerError('Error creating new schedule')    

    # Display the schedule in question
    return redirect(f'schedules/{schedule.id}')

@login_required
@require_http_methods(["GET","POST"])
def create(request):
    """
    Creates a new schedule, when requested via POST.
    Requires no contents in request body.
    """

    # if (accidental) GET request, redirect to index view
    if request.method == 'GET':
        return redirect('/')

    # Check if user already has max number of schedules
    sched_list = Schedule.objects.filter(user=request.user)
    if len(sched_list) >= MAX_SCHEDULES:
        return JsonResponse({'msg': 'Maximum schedules reached'},status=403)
    
    # Create new schedule, save to DB, and return ID
    try:
        schedule = sl.new(request.user)
        schedule.save()
    except Exception as e:
        print(e) # TODO: turn this into a logging statement
        return JsonResponse({'msg': 'Error creating schedule'}, status=500)

    return JsonResponse({'msg': 'Schedule created', 'schedule': schedule.id},status=200)

@login_required
def sched_router(request, sched_id):
    """
    Handles requests to schedule pages ("/:id").
    Dispatches to a handler based on request method.
    """
    if sched_id is None:
        return redirect('/')
    
    if request.method == 'GET':
        return display(request, sched_id)
    elif request.method == 'DELETE':
        return delete(request, sched_id)
    elif request.method == 'POST':
        return update_title(request)
    elif request.method == 'PATCH':
        return update_schedule(request)
    else:
        return HttpResponseNotAllowed(['GET', 'POST', 'DELETE', 'PATCH'])


def display(request, sched_id):
    """
    Displays a specific schedule page ("/:id").
    """

    # Obtain all schedules for this user (to pass to template)
    sched_list = Schedule.objects.filter(user=request.user)

    # Pull requested schedule using ID and user
    try:
        schedule = sched_list.get(id=sched_id)
    except Schedule.DoesNotExist:
        return HttpResponseBadRequest('Schedule not found')

    # Load context and render template
    context = sl.existing(schedule, request.user, sched_list)
    return render(request, 'planner/index.html', context)

def update_schedule(request): 
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

def delete(request, sched_id):
    """
    Deletes a schedule from the database.
    """
    # Grab schedule object from DB
    try: 
        schedule = Schedule.objects.filter(user=request.user).get(id=sched_id)
    except Schedule.DoesNotExist:
        return HttpResponseBadRequest('Schedule not found')
    
    # Delete schedule from DB
    try: 
        schedule.delete()
    except Exception as e:
        return HttpResponseServerError('Error deleting schedule' + str(e))
    
    # Confirm successful deletion
    return HttpResponse(status=204)

def update_title(request):
    """
    Updates the title of a given schedule. 
    """
    form = TitleForm(request.POST)

    if not form.is_valid():
        return HttpResponseBadRequest('Invalid form!')

    sched_id = form.cleaned_data['sched_id']
    title = form.cleaned_data['title']

    if title is None:
        return HttpResponseBadRequest('Title not found')
    
    try:
        schedule = Schedule.objects.filter(user=request.user).get(id=sched_id)
    except Schedule.DoesNotExist:
        return HttpResponseBadRequest('Schedule not found')

    schedule.name = title
    try:
        schedule.save()
    except Exception as e:
        print(e) # TODO: turn this into a logging statement
        return HttpResponseServerError('Error saving schedule')
    
    return redirect(f'/?id={schedule.id}')