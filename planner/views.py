import json
import planner.utils.schedloader as sl
import planner.utils.schedupdater as su
from django.shortcuts import HttpResponse, render, redirect
from django.template import loader
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseBadRequest, HttpResponseServerError
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_safe
from planner.models import Course, Schedule, Course_Schedule, Prereq
from planner.forms import TitleForm

@require_safe
def index(request):
    """
    Takes requests to index URL ("/"), and redirects to a scheduler page ("/:id"). 
    Loads a demo page if user is unauthenticated. 
    Creates a schedule for the user if none exists. 
    """

    # If user is logged out, show 'demo' schedule
    if not request.user.is_authenticated:
        return render(request, 'planner/index.html', sl.demo())

    # Check for existing schedules for this user
    sched_list = Schedule.objects.filter(user=request.user)
    # If none exist, create a new one
    if not sched_list.exists():
        try:
            schedule = sl.new(request.user)
            schedule.save()
        except:
            return HttpResponseServerError('Error creating new schedule')
    # otherwise, load most recently created
    else:
        schedule = sched_list.last()

    # Redirect to the schedule's index page
    return redirect(f'schedule/{schedule.id}')

@login_required
def router(request, sched_id):
    if sched_id is None:
        return redirect('/')

    if request.method == 'GET':
        return schedule(request, sched_id)
    elif request.method == 'DELETE':
        return delete(request, sched_id)
    elif request.method == 'PATCH':
        # check if form included is a title update or schedule body update
        # call appropriate handler
        pass


@login_required
@require_safe
def schedule(request, sched_id):
    """
    Handles requests in the format "/:sched_id", where sched_id is the ID of an existing schedule.
    Rejects unauthenticated requests or schedules which do not exist/are not this user's.
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
def delete(request, sched_id):
    """
    Deletes the schedule with the passed ID, provided
    it exists and is owned by the requesting user. 
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

@login_required
@require_http_methods(["POST"])
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
    schedule.save()
    
    return redirect(f'/?id={schedule.id}')