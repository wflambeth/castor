
from planner.models import Course, Schedule, Course_Schedule, Prereq
from planner.forms import TitleForm
from datetime import datetime

def demo():
    """ Creates and returns rendering context for demo scheduler page.

    Called by planner/views.py/index().
    
    For use with non-authenticated users; cannot be used to save changes. 
    Does not create any new DB objects - only reads existing course info
    and passes dummy values for schedule name/qtrs/ID.
    
    Returns:
        dict containing all data needed to render course-planner HTML template,
        including courses/prereqs and a default span of four quarters.

    """
    year = datetime.now().year
    prereqs, quarters, indices = data_context_builder()

    context = {
        "sched_id": -1,
        "sched_name": "Demo Schedule",
        "unsched_req": Course.objects.filter(required=True),
        "unsched_elec": Course.objects.filter(required=False),
        "sched_qtrs": {
            (year,0): [],
            (year,1): [], 
            (year,2): [],
            (year,3): []
        },
        "prereqs": prereqs,
        "quarters": quarters,
        "indices": indices,
    }

    return context

def new(user):
    """Builds new schedule object owned by the provided User.

    Called by planner/views.py/create(). Does not save schedule to DB;
    this is handled in parent view.

    Args:
        user: a DB User object
    
    Returns:
        ORM Schedule object owned by that User, with default values 
        (no courses scheduled, four terms consisting of current calendar year).
    """
    year = datetime.now().year

    schedule = Schedule (
        user = user,
        start_qtr = 0,
        end_qtr = 3,
        start_year = year,
        end_year = year
    )

    return schedule


def existing(schedule, user, sched_list):
    """Loads an existing schedule from DB, along with rendering context.

    Called by planner/views.py/display().

    Args:
        schedule: DB Schedule object to be loaded
        user: DB User object who owns the schedule
        sched_list: DB QuerySet of schedules owned by the user

    Returns:
        dict containing schedule's current state and all context
        needed to render course-planner HTML template.

    """
    # Pull all courses, separated into scheduled and unscheduled
    # (Only scheduled courses are associated with the schedule in the DB)
    sched_courses = Course_Schedule.objects.filter(schedule=schedule).order_by('course__course_number')
    unsched_courses = Course.objects.all().exclude(course_number__in=sched_courses.values('course'))

    # Obtain dicts of course prereqs/quarters offered, initialize
    # dict of course indices (for tracking where courses are placed)
    prereqs, quarters, indices = data_context_builder()

    # Iterate over quarters of schedule from start to finish,
    # appending courses which have been scheduled in each. 
    sched_qtrs = {}
    qtr = schedule.start_qtr
    year = schedule.start_year
    
    while year <= schedule.end_year:
        if year == schedule.end_year and qtr > schedule.end_qtr:
            break
        
        # tuple of year_qtr is used as key for each term in schedule; value is an array 
        # of the scheduled courses. (Probably could stand a refactor, it's a bit much.)
        sched_qtrs[(year, qtr)] = []
        for course in sched_courses.filter(year=year, qtr=qtr):
            sched_qtrs[(year, qtr)].append(course)
        
        qtr = qtr + 1 if qtr < 3 else 0 
        if qtr == 0: 
            year += 1
    
    context = {
        "user": user,
        "sched_list": sched_list,
        "sched_id": schedule.id,
        "sched_name": schedule.name,
        "unsched_req": unsched_courses.filter(required=True),
        "unsched_elec": unsched_courses.filter(required=False),
        "sched_qtrs": sched_qtrs,
        "prereqs": prereqs,
        "quarters": quarters,
        "indices": indices,
        "form": TitleForm(initial={'sched_id': schedule.id, 'title': schedule.name})
    }

    return context


def data_context_builder():
    """ Used by new() and existing() to build context for rendering page.
    
    Stores information on course prereqs and quarters offered, for use 
    by client-side JS. Also initializes an "indices" dict for tracking
    where courses are placed in the schedule.

    Returns:
        prereqs:  dict mapping course numbers to lists of prereq course numbers
        quarters: dict mapping course numbers to lists of quarters offered
        indices:  dict mapping course numbers to where they are placed in schedule 
                  (initialized to -1, indicating unscheduled)

    """
    prereqs = {}
    quarters = {}
    indices = {}
    for course in Course.objects.all():
        prereqs[course.course_number] = [prereq.prereq.course_number for prereq in Prereq.objects.filter(course=course)]
        quarters[course.course_number] = course.qtrs
        indices[course.course_number] = -1 

    return prereqs, quarters, indices
