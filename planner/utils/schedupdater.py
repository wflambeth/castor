from planner.models import Course, Course_Schedule

def update(schedule, courses, dates):
    print(dates)

    # check if start/end terms have changed (are not null), update if so
    if dates['start']['year'] and dates['start']['qtr']:
        schedule.start_year = dates['start']['year']
        schedule.start_qtr = dates['start']['qtr']

    if dates['end']['year'] and dates['end']['qtr']:
        schedule.end_year = dates['end']['year']
        schedule.end_qtr = dates['end']['qtr']
    
    schedule.save()

    for crs_num, term in courses.items():
        course = Course.objects.get(course_number=int(crs_num))

        # Pull existing course-schedule relationship if it exists, or create one if not
        try:
            crs_sch = Course_Schedule.objects.get(schedule=schedule, course=course)
        except Course_Schedule.DoesNotExist:
            crs_sch = Course_Schedule(schedule=schedule, course=course)

        # if course is to be removed from schedule, do so and move on
        if not term['year'] or term['year'] == 'null':
            crs_sch.delete()
        # otherwise, update year/qtr as specified
        else:
            crs_sch.year = term['year']
            crs_sch.qtr = term['qtr']
            crs_sch.save()