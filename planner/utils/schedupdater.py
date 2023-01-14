from planner.models import Course, Course_Schedule

def update(schedule, courses):
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