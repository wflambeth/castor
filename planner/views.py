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
    Loads a demo page (if user is unauthenticated), or the most recently created schedule for the user.
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
        schedule = sched_list[-1]

    # Redirect to the schedule's index page
    return redirect('schedule', sched_id=schedule.id)

@login_required
def router(request, sched_id):
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
    
    if sched_id is None:
        return redirect('/')

    # Obtain all schedules for this user (to pass to template)
    sched_list = Schedule.objects.filter(user=request.user)

    # Pull requested schedule using ID and user
    try:
        schedule = sched_list.get(id=sched_id)
    except Schedule.DoesNotExist:
        # TODO: should this just redirect to index?
        return HttpResponseBadRequest('Schedule not found')

    # Load context, adding: user object, list of user schedules, retitling form
    context = sl.existing(schedule)
    context['user'] = request.user
    context['sched_list'] = sched_list
    context['form'] = TitleForm(initial={'sched_id': schedule.id, 'title': schedule.name})
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
    return redirect('schedule', sched_id=schedule.id)

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