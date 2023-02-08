
from planner.models import Course, Schedule, Course_Schedule, Prereq
from datetime import datetime

def demo():
    """
    If user is not logged in, create an empty schedule with 4 terms covering the current year. 
    """
    year = datetime.now().year
    context = {
        "unsched_req": Course.objects.filter(required=True),
        "unsched_elec": Course.objects.filter(required=False),
        "sched_qtrs": {
            (year,0): [],
            (year,1): [], 
            (year,2): [],
            (year,3): []
        }
    }

    return context

def existing(schedule):
    """
    Loads an existing schedule from DB, along with needed context for rendering course-planner HTML template. 
    """
    # Pull all courses, separated into scheduled and unscheduled
    # (Only scheduled courses are associated with the schedule in the DB)
    sched_courses = Course_Schedule.objects.filter(schedule=schedule).order_by('course__course_number')
    unsched_courses = Course.objects.all().exclude(course_number__in=sched_courses.values('course'))
    # Context for rendering page/tracking changes; see data_context_builder below
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
        "schedule": schedule,
        "unsched_req": unsched_courses.filter(required=True),
        "unsched_elec": unsched_courses.filter(required=False),
        "sched_qtrs": sched_qtrs,
        "prereqs": prereqs,
        "quarters": quarters,
        "indices": indices,
    }

    return context

def new(user):
    """
    Builds new Schedule object, owned by the given User object, with default values 
    (no courses scheduled, four terms consisting of current calendar year).

    Does not save Schedule to DB; this is handled in views.create(), which calls this method. 
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

def data_context_builder():
    """
    Loads current info from DB on: 
    - prerequisites
    - quarters
    
    Also initializes "indices" dict, tracks location of all saved courses.

    Doing them all at once to minimize DB calls/consolidate iteration. 
    """
    prereqs = {}
    quarters = {}
    indices = {}
    for course in Course.objects.all():
        prereqs[course.course_number] = [prereq.prereq.course_number for prereq in Prereq.objects.filter(course=course)]
        quarters[course.course_number] = course.qtrs
        indices[course.course_number] = -1 # default value for unsaved courses; overwritten by script as page loads.

    return prereqs, quarters, indices
