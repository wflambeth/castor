import json
from planner.utils.ScheduleUtils import ScheduleLoader, ScheduleUpdater
from django.shortcuts import HttpResponse, render, redirect
from django.http import HttpRequest, JsonResponse, HttpResponseBadRequest,\
                        HttpResponseServerError, HttpResponseNotAllowed
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_safe
from planner.models import Schedule
from planner.forms import TitleForm

MAX_USER_SCHEDULES = 10

@require_safe
def index(request: HttpRequest) -> HttpResponse:
    """Handles requests to the index page ("/").
    
    If user is logged in, displays their most recently created schedule. 
    If user is logged out, displays a demo schedule.
    """
    sl = ScheduleLoader()

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
def create(request: HttpRequest) -> JsonResponse:
    """Handles requests to create a new schedule ("/schedules").

    Intended to handle POST requests; GET requests assumed to 
    be accidental and redirected to "/".

    Args:
        request: XHR POST request from index page JS
    
    Returns:
        JSON response with new schedule ID or error message
    """
    sl = ScheduleLoader()

    # if GET request, redirect to index view
    if request.method == 'GET':
        return redirect('/')

    # Check if user already has max number of schedules
    sched_list = Schedule.objects.filter(user=request.user)
    if len(sched_list) >= MAX_USER_SCHEDULES:
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
def sched_router(request: HttpRequest, sched_id: int = None) -> HttpResponse:
    """Handles requests to a specific schedule ("/schedules/:id").

    Routes to appropriate view function based on request method.
    """
    if sched_id is None:
        return redirect('/')
    
    if request.method == 'GET':
        # Show schedule
        return display(request, sched_id)
    elif request.method == 'DELETE':
        # Delete schedule
        return delete(request, sched_id)
    elif request.method == 'POST':
        # Update schedule title
        return update_title(request)
    elif request.method == 'PATCH':
        # Update schedule contents
        return update_schedule(request)
    else:
        return HttpResponseNotAllowed(['GET', 'POST', 'DELETE', 'PATCH'])


def display(request: HttpRequest, sched_id: int) -> HttpResponse:
    """Displays schedule viewer/editor page for a given schedule,
       upon GET request.
    """
    sl = ScheduleLoader()

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

def update_schedule(request: HttpRequest) -> JsonResponse: 
    """ Handles requests to update a schedule's contents.

    Args:
        request: XHR PATCH request from index page JS, including
                 JSON list of courses and terms to update

    Returns:
        JSON response with status and schedule ID

    """
    su = ScheduleUpdater()

    data = json.loads(request.body)
    try:
        schedule = Schedule.objects.filter(user=request.user).get(id=int(data['s']))
    except Schedule.DoesNotExist:
        return HttpResponseBadRequest('Schedule not found')
    
    try:
        su.update(schedule, data['courses'], data['dates'])
    except Exception as e:
        print("Error saving schedule updates", e)
        return JsonResponse({'status': 'failed', 'schedule': schedule.id}, status=500)

    return JsonResponse({'status': 'saved', 'schedule': schedule.id}, status=200)

def delete(request: HttpRequest, sched_id: int) -> HttpResponse:
    """Deletes a given schedule from the database.

    Args:
        request: XHR DELETE request from index page JS
    
    Returns:
        JSON response with status of deletion

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

def update_title(request: HttpRequest) -> HttpResponse:
    """Updates the title of a given schedule.

    Args:
        request: XHR POST request from index page JS, including
                 Django form object
    
    Returns:
        Redirect to index page with updated schedule ID, 
        or HTTP error code if invalid form/DB error

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