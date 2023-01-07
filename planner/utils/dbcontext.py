
from planner.models import Course, Schedule, Course_Schedule, Prereq
from datetime import datetime

def no_auth():
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
