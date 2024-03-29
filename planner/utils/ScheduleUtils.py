
from planner.models import Course, User, Schedule, Course_Schedule, Prereq
from planner.forms import TitleForm
from datetime import datetime


def _data_context_builder() -> tuple[dict, dict, dict]:
    """ Used by new() and existing() to build context for rendering page.

    Pulls live DB snapshot of course prereqs and quarters offered, for use 
    by client-side JS. Also initializes an "indices" dict for tracking
    where courses are placed in the schedule.

    Returns:
        prereqs:  dict mapping course numbers to lists of prereq course numbers
        offered_qtrs: dict mapping course numbers to lists of quarters offered
        indices:  dict mapping course numbers to where they are placed in schedule 
                (initialized to -1, indicating unscheduled)

    """

    # TODO: Combine into single dict
    prereqs = {}
    offered_qtrs = {}
    indices = {}
    for course in Course.objects.all():
        crs_num = course.course_number

        prereqs[crs_num] = [prereq.prereq.course_number for
                            prereq in Prereq.objects.filter(course=course)]
        offered_qtrs[crs_num] = course.qtrs
        indices[crs_num] = -1

    return prereqs, offered_qtrs, indices


def get_context_demo() -> dict:
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
    prereqs, offered_qtrs, indices = _data_context_builder()

    context = {
        "sched_id": -1,
        "sched_name": "Demo Schedule",
        "unsched_req": Course.objects.filter(required=True),
        "unsched_elec": Course.objects.filter(required=False),
        "sched_qtrs": {
            (year, 0): [],
            (year, 1): [],
            (year, 2): [],
            (year, 3): []
        },
        "prereqs": prereqs,
        "offered_qtrs": offered_qtrs,
        "indices": indices,
        "credits": 0
    }

    return context

# TODO: install 'django-stubs' package for type-hinting Django QuerySets


def get_context_existing(schedule: Schedule, user: User, sched_list: any) -> dict:
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
    sched_courses = Course_Schedule.objects.filter(
        schedule=schedule).order_by('course__course_number')
    unsched_courses = Course.objects.all().exclude(
        course_number__in=sched_courses.values('course'))

    # Obtain dicts of course prereqs/quarters offered, initialize
    # dict of course indices (for tracking where courses are placed)
    prereqs, offered_qtrs, indices = _data_context_builder()

    # Iterate over quarters of schedule from start to finish,
    # appending courses which have been scheduled in each.
    sched_qtrs = {}
    credits = 0
    qtr = schedule.start_qtr
    year = schedule.start_year

    while year <= schedule.end_year:
        if year == schedule.end_year and qtr > schedule.end_qtr:
            break

        # tuple of year_qtr is used as key for each term in schedule; value is an array
        # of the scheduled courses. (Probably could stand a refactor, it's a bit much.)
        sched_qtrs[(year, qtr)] = []
        for course in sched_courses.filter(year=year, qtr=qtr):
            credits += course.course.credits
            sched_qtrs[(year, qtr)].append(course)

        qtr = qtr + 1 if qtr < 3 else 0
        if qtr == 0:
            year += 1

    # Create context dict and return
    context = {
        "user": user,
        "sched_list": sched_list,
        "sched_id": schedule.id,
        "sched_name": schedule.name,
        "unsched_req": unsched_courses.filter(required=True),
        "unsched_elec": unsched_courses.filter(required=False),
        "sched_qtrs": sched_qtrs,
        "prereqs": prereqs,
        "offered_qtrs": offered_qtrs,
        "indices": indices,
        "credits": credits,
        "form": TitleForm(initial={'title': schedule.name})
    }

    return context


def new_schedule(user: User) -> Schedule:
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

    schedule = Schedule(
        user=user,
        start_qtr=0,
        end_qtr=3,
        start_year=year,
        end_year=year
    )

    return schedule


def update_schedule(schedule: Schedule, courses: list[int], dates: dict[dict]) -> None:
    """ Updates a schedule's contents in the database.

    Called by planner/views.py/update_schedule(). Parses JSON data from
    XHR PATCH request and modifies Course/Course_Schedule objects accordingly.
    Only changes to previously saved schedule are included in request.

    Args:
        schedule: Schedule object to be updated
        courses: list of courses to be updated
        dates: dict representing schedule start/end dates

        dates structure:
            {start: {'year': int,'qtr': int },
                end:   {'year': int,'qtr': int }}
    """

    # Update schedule start dates (if modified)
    if dates['start']['year'] is not None and dates['start']['qtr'] is not None:
        print(dates)
        schedule.start_year = dates['start']['year']
        schedule.start_qtr = dates['start']['qtr']

    # Update schedule end dates (if modified)
    if dates['end']['year'] is not None and dates['end']['qtr'] is not None:
        print(dates)
        schedule.end_year = dates['end']['year']
        schedule.end_qtr = dates['end']['qtr']

    # Save date changes to Schedule object in DB
    schedule.save()

    # Iterate over items in courses list, updating Course_Schedule objects
    for crs_num, term in courses.items():
        course = Course.objects.get(course_number=int(crs_num))

        # If course is to be deleted
        if not term['year'] or term['year'] == 'null':
            # Pull existing course-schedule relationship and delete
            try:
                crs_sch = Course_Schedule.objects.get(
                    schedule=schedule, course=course)
                crs_sch.delete()
            # If not yet saved, no problem; move on
            except Course_Schedule.DoesNotExist:
                continue

        # Otherwise, course is to be added/moved
        else:
            try:
                crs_sch = Course_Schedule.objects.get(
                    schedule=schedule, course=course)
            except Course_Schedule.DoesNotExist:
                crs_sch = Course_Schedule(schedule=schedule, course=course)

            # Update year/qtr as specified
            crs_sch.year = term['year']
            crs_sch.qtr = term['qtr']
            crs_sch.save()
