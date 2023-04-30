from planner.models import Course, Course_Schedule

def update(schedule, courses, dates):
    """ Updates a schedule's contents in the database.

    Called by planner/views.py/update_schedule(). Parses JSON data from
    XHR PATCH request and modifies Course/Course_Schedule objects accordingly.
    Only changes to previously saved schedule are included in request.

    Args:
        schedule: ORM Schedule object to be updated
        courses: JSON list of courses to be updated
        dates: JSON representing schedule start/end dates

    Returns:
        None (updates DB directly. Raises exception if error encountered)

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

        # Pull existing course-schedule relationship if it exists
        try:
            crs_sch = Course_Schedule.objects.get(schedule=schedule, course=course)
        # Create new relationship if it doesn't
        except Course_Schedule.DoesNotExist:
            crs_sch = Course_Schedule(schedule=schedule, course=course)

        # if course is to be removed from schedule, do so
        if not term['year'] or term['year'] == 'null':
            crs_sch.delete()
        # otherwise, update year/qtr as specified
        else:
            crs_sch.year = term['year']
            crs_sch.qtr = term['qtr']
            crs_sch.save()