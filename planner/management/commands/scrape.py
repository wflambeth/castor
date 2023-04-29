import json, requests
from string import capwords
from datetime import datetime
from zoneinfo import ZoneInfo
from attrs import define, field, asdict
from bs4 import BeautifulSoup, Comment
from django.core.management.base import BaseCommand
from planner.models import Course, Prereq

# URL and start snippet for locating course JSON
URL = 'https://ecampus.oregonstate.edu/soc/ecatalog/ecourselist.htm?termcode=all&subject=CS'
START = '[{"SubjectCode":"CS","CourseNumber":'
# List of courses to ignore when scraping (not applicable to postbac track)
FOUR_YEAR_ONLY = [101, 151, 165, 175, 201, 461, 462, 463]
# For translating course quarter codes into DB representation
QTRS = {'W': 0, 'Sp': 1, 'Su': 2, 'F': 3}

class Command(BaseCommand):
    """
    """
    def scrape_json(self):
        """
        """
        response = requests.get(URL)
        soup = BeautifulSoup(response.text, 'html.parser')
        comments = soup.find_all(string=lambda text: isinstance(text, Comment))
        for comment in comments:
            if START in comment:
                return comment
    
    # Build list of CourseItem dataclass instances from scraped JSON
    def build_scraped_courses(self, scraped_data):
        """
        """
        courses = []

        # Iterate over raw JSON-loaded data, storing in dataclass
        for course in scraped_data:
            if CourseInfo.is_valid_postbac_course(course['CourseNumber']):
                # Wrap single-session courses in a list for format consistency
                if type(course['Offerings']['CourseOffering']) is dict:
                    sessions = [course['Offerings']['CourseOffering']]
                else:
                    sessions = course['Offerings']['CourseOffering']

                # Conversion/validation handled in dataclass; see below
                courses.append(CourseInfo.from_scraped(sessions))
        
        return courses
    
    # Format a given course's prereqs (from DB) as a sorted list
    def build_db_prereq_list(self, course_number):
        """
        TODO: Just put this back in the main function? 
        """
        prereq_vals = Prereq.objects.filter(course=course_number).values_list("prereq")
        prereq_list = sorted([prereq[0] for prereq in prereq_vals])

        return prereq_list
    
    # Write details of any data mismatch to logs
    def print_discrepancy(self, key, course, scrape_val, db_val):
        """
        """
        self.stdout.write(str(course) + ' ' + " has changed " + str(key).upper())
        self.stdout.write("DB     : " + str(db_val))
        self.stdout.write("Scraped: " + str(scrape_val) + '\n\n')        
    
    def handle(self, *args, **options):
        """
        """
        # Begin logging output, with timestamp
        self.stdout.write("********** SCRAPING ECAMPUS CATALOG **********")
        dt = datetime.now(ZoneInfo('US/Pacific'))
        self.stdout.write(dt.strftime("%Y-%m-%d %H:%M:%S") + " Pacific" + '\n\n')

        # Scrape course data from JSON, build list of CourseInfo dataclass instances
        course_json = self.scrape_json()
        scraped_data = json.loads(course_json)
        scraped_courses = self.build_scraped_courses(scraped_data)

        # Pull stored course and prereq data
        db_courses = list(Course.objects.all().values())
        db_prereqs = Prereq.objects.all()

        # Iterate over DB vs scraped courses and compare
        i = j = 0
        l = max(len(scraped_courses), len(db_courses))
        issue_ct = 0
        while i < l and j < l:
            # Ensure that course numbers are same
            if scraped_courses[i].course_number != db_courses[j]['course_number']:
                # If scraped course is not yet in DB, log and iterate past
                if scraped_courses[i].course_number < db_courses[j]['course_number']:
                    self.stdout.write("NEW COURSE: " + 
                                      str(scraped_courses[i].course_number) + 
                                      ' ' + scraped_courses[i].title + '\n\n')
                    i += 1
                    issue_ct += 1
                    continue
                # If DB course is missing from scrape, log and iterate past
                else:
                    self.stdout.write("STALE COURSE: " + 
                                      str(db_courses[j]['course_number']) + 
                                      ' ' +  db_courses[j]['title'] + '\n\n')
                    j += 1
                    issue_ct += 1
                    continue
            
            # Compare quarters/credits/titles, logging any differences
            for key in ['title', 'credits', 'qtrs']:
                if asdict(scraped_courses[i])[key] != db_courses[j][key]:
                    self.print_discrepancy(key, scraped_courses[i].course_number, 
                                           db_courses[j][key], asdict(scraped_courses[i])[key])
                    issue_ct += 1
            
            # Build prereq lists for this course
            db_prereqs = self.build_db_prereq_list(db_courses[j]['course_number'])
            scraped_prereqs = sorted(scraped_courses[i].prereqs)
            # Compare prereqs, logging any differences
            if db_prereqs != scraped_prereqs:
                self.print_discrepancy('prereq', scraped_courses[i].course_number, 
                                        db_courses[j][key], asdict(scraped_courses[i])[key])
                issue_ct += 1
            
            # After comparisons, iterate forward in both course lists
            i += 1
            j += 1
        
        # Print completion message and count of errors found
        self.stdout.write("**********SCRAPING COMPLETED. " + str(issue_ct) + " ISSUE(S) FOUND**********")


@define
# TODO: throw all the properties at the top here? 
class CourseInfo:
    """
    
    """
    def _normalize_title(title):
        """Intake formatter for course titles. 

        Args:
            title: A string extracted from raw scraped JSON
        
        Returns:
            The same string, with proper capitalization and 
            devoid of leading non-alphanumeric characters.

        """
        # Strip leading non-alnum chars
        i = 0
        while not title[i].isalnum():
            i += 1
        if i > 0:
            title = title[i:]

        title = capwords(title)
        # This avoids titles like "Software Engineering Ii"
        if title[-2:] == 'Ii':
            return title[:-1] + "I"
        
        return title
    
    def _normalize_credits(credits):
        """Intake formatter for course credits.

        Takes in a string and returns its integer representation.
        In situations where a range of credits is possible ("1-16"), string
        will throw an error; in those cases, returns lowest value in range.
        
        """
        try:
            return int(credits)
        except ValueError:
            return int(credits[0])
        
    # Course number
    course_number: int = field(converter=int)
    
    # Course title
    title: str = field(converter=_normalize_title)

    # No. of Credits
    credits: int = field(converter=_normalize_credits)

    # Quarters offered
    qtrs: list[int] = field(converter=lambda x: sorted(list(set(x))))

    # Prerequisites
    prereqs: list[int] = field(converter=lambda x: sorted(list(set(x))))

    @classmethod
    def is_valid_postbac_course(self, course_number):
        # Ignore honors courses (not postbac; have trailing 'H')
        try:
            course_number = int(course_number)
        except ValueError:
            return False

        # Ignore four-year degree courses
        if course_number in FOUR_YEAR_ONLY:
            return False
        # Ignore graduate-level courses
        elif course_number > 499:
            return False
        else:
            return True

    @classmethod 
    def extract_prereqs(self, offerings):
        """Builds a table of prerequisite

        """
        prereqs = []
        for offering in offerings:
            # Avoids issues with non-course entities (e.g. placement tests)
            if 'Prereqs' in offering:
                prq_list = offering['Prereqs']['CoursePrereq']
                # wraps single-item results in a list for formatting consistency
                if type(prq_list) is dict:
                    prq_list = [prq_list]

                for prq in prq_list:
                    # Ensures prereq is also a valid postbac course
                    if ('PrereqSubjectCode' in prq and prq['PrereqSubjectCode'] == 'CS' and 
                        self.is_valid_postbac_course(prq['PrereqCourseNumber'])):
                        # if so, append to output list
                        prereqs.append(int(prq['PrereqCourseNumber']))

        return prereqs

    # Pulls course data from an array of course offerings (in JSON scraped from catalog)
    @classmethod
    def from_scraped(self, offerings):
        """
        Source JSON is messy, these indices are how we pull it out

        """
        return CourseInfo(
            course_number = offerings[0]['CourseNumber'],
            qtrs = [ QTRS[offering['TermShortDescription'][:-2]] for offering in offerings ],
            title = offerings[0]['Title'],
            credits = offerings[0]['Credits'],
            prereqs = CourseInfo.extract_prereqs(offerings)
        )