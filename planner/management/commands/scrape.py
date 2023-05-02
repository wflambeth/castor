import json
import requests
import logging
from string import capwords
from attrs import define, field, asdict
from bs4 import BeautifulSoup, Comment
from django.core.management.base import BaseCommand
from planner.models import Course, Prereq

logger = logging.getLogger(__name__)

QTRS = {'W': 0, 'Sp': 1, 'Su': 2, 'F': 3}
# URL for eCampus catalog scraping
URL = 'https://ecampus.oregonstate.edu/soc/ecatalog/ecourselist.htm?termcode=all&subject=CS'
# String to locate JSON within catalog HTML
START = '[{"SubjectCode":"CS","CourseNumber":'
# Courses that are not offered in postbac track (ignored when scraping)
FOUR_YEAR_ONLY = [101, 151, 165, 175, 201, 295, 461, 462, 463]


@define
class CourseInfo:
    """Dataclass for converting/validating/storing scraped course data.

    Uses the attrs package to extend built-in dataclass functionality.

    Public methods:
        CourseInfo.from_scraped() - Builds CourseInfo instance from scraped course data
        CourseInfo.is_valid_postbac_course() - Checks if course is valid for postbac track
        CourseInfo.extract_prereqs() - Extracts valid prereqs from scraped prereq data

    """
    @staticmethod
    def _format_title(title: str) -> str:
        """Intake formatter for course titles. 

        Args:
            title: A string extracted from raw scraped JSON

        Returns:
            The same string, with capitalization corrected and 
            leading characters stripped. 

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

    @staticmethod
    def _format_credits(credits: str) -> int:
        """Intake formatter for course credits.

        Args:
            credits: A course number extracted from scraped data

        Returns:
            An int representing the number of credits for the course
            (If credits are variable, returns the minimum number of credits)

        """
        try:
            return int(credits)
        except ValueError:
            return int(credits[0])

    course_number: int = field(converter=int)
    title: str = field(converter=_format_title)
    credits: int = field(converter=_format_credits)
    qtrs: list[int] = field(converter=lambda x: sorted(list(set(x))))
    prereqs: list[int] = field(converter=lambda x: sorted(list(set(x))))

    @classmethod
    def is_valid_postbac_course(cls, course_number: int) -> bool:
        """Checks if course is valid for postbac track.

        Args:
            course_number: The course number of the course in question

        Returns:
            Boolean indicating valid/invalid course

        """

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
    def extract_prereqs(cls, offerings: list[dict]) -> list[int]:
        """Extracts valid prereqs from scraped prereq data.

        Attrs:
            offerings: A list of dicts, each containing course data

        Returns:
            A list of valid prereq course numbers for that course

        """
        prereqs = []
        for offering in offerings:
            # Non-course entities (e.g. placement tests) do not have a 'Prereqs' key
            if 'Prereqs' in offering:
                prq_list = offering['Prereqs']['CoursePrereq']
                # wrap single-item results in a list for type consistency
                if type(prq_list) is dict:
                    prq_list = [prq_list]

                for prq in prq_list:
                    # Check that prereq is also a valid postbac course
                    if ('PrereqSubjectCode' in prq and prq['PrereqSubjectCode'] == 'CS' and
                            cls.is_valid_postbac_course(prq['PrereqCourseNumber'])):
                        # if so, append to output list
                        prereqs.append(int(prq['PrereqCourseNumber']))

        return prereqs

    # Pulls course data from an array of course offerings (in JSON scraped from catalog)
    @classmethod
    def from_scraped(cls, offerings: list[dict]) -> 'CourseInfo':
        """Initializes a CourseInfo instance from a scraped course data record.
        """
        return CourseInfo(
            course_number=offerings[0]['CourseNumber'],
            qtrs=[QTRS[offering['TermShortDescription'][:-2]]
                  for offering in offerings],
            title=offerings[0]['Title'],
            credits=offerings[0]['Credits'],
            prereqs=CourseInfo.extract_prereqs(offerings)
        )


class Command(BaseCommand):
    """Contains methods for scraping course data from OSU's eCampus catalog.

    handle() is called via 'python manage.py scrape' from the command line, 
    and is the only public method. 
    """

    def handle(self, *args, **options) -> None:
        """Method for running scrape, called via 'python manage.py scrape' 
            from the command line. 

        'args'/'options' arguments are required per Django syntax, but are unused.        
        """
        # Begin logging output, with timestamp
        logger.info("SCRAPING ECAMPUS CATALOG")

        # Scrape course data from JSON, load into memory
        course_json = self._scrape_json()
        scraped_data = json.loads(course_json)

        # Build list of courses from each source
        scraped_courses = self._build_scraped_courses(scraped_data)
        db_courses = list(Course.objects.all().values())

        # Compare contents and check for any issues 
        # (Individual issues are also printed to logs in _compare_course_lists)
        issue_ct = self._compare_course_lists(scraped_courses, db_courses)

        # Log scrape completion and # of issues found
        if issue_ct == 0:
            logger.info("SCRAPING COMPLETED. NO ISSUES FOUND")
        else:
            logger.warning("SCRAPING COMPLETED. " +
                           str(issue_ct) + " ISSUE(S) FOUND")

    @staticmethod
    def _scrape_json() -> str:
        """Locates and scrapes course info JSON from Ecampus catalog. 
        """
        response = requests.get(URL)
        soup = BeautifulSoup(response.text, 'html.parser')
        comments = soup.find_all(string=lambda text: isinstance(text, Comment))
        for comment in comments:
            if START in comment:
                return comment

    @staticmethod
    def _build_scraped_courses(scraped_data: list[dict]) -> list[CourseInfo]:
        """Builds a list of CourseInfo dataclass instances from converted JSON.

        Args:
            scraped_data (list): A list of dicts, each containing course data

        Returns:
            List of CourseInfo dataclass instances, one per course in scraped_data
        """
        courses = []

        # Iterate over raw JSON-loaded data, storing in dataclass
        for course in scraped_data:
            if CourseInfo.is_valid_postbac_course(course['CourseNumber']):
                # Wrap single-session courses in a list for type consistency
                if type(course['Offerings']['CourseOffering']) is dict:
                    sessions = [course['Offerings']['CourseOffering']]
                else:
                    sessions = course['Offerings']['CourseOffering']

                # Conversion/validation handled by dataclass
                courses.append(CourseInfo.from_scraped(sessions))

        return courses

    @staticmethod
    def _build_db_prereq_list(course_number: int) -> list[int]:
        """Builds prereq list from DB for a given course. 

        Args:
            course_number: The course number whose prereqs are needed

        Returns:
            A sorted list of prereq course numbers for that course, as stored in DB. 

        """
        prereq_vals = Prereq.objects.filter(course=course_number).values_list("prereq")
        prereq_list = sorted([prereq[0] for prereq in prereq_vals])

        return prereq_list

    def _compare_course_lists(self, scraped_courses: list, db_courses: list) -> int:
        """Iterates over contents of scrape and course database, flagging errors.

        Args:
            scraped_courses: List of CourseInfo objects 
            db_courses: List of dicts holding data from DB Course objects
        
        Returns:
            int representing the number of discrepancies found
        
        """
        
        # Initialize parameters for comparison loop
        i = j = 0
        course_ct = max(len(scraped_courses), len(db_courses))
        issue_ct = 0

        # Loop over scrape/db contents and compare
        while i < course_ct and j < course_ct:
            # First ensure that course numbers are same
            if scraped_courses[i].course_number != db_courses[j]['course_number']:
                # If scraped course is not yet in DB, log and iterate past
                if scraped_courses[i].course_number < db_courses[j]['course_number']:
                    logger.warning("NEW COURSE: " +
                                   str(scraped_courses[i].course_number) +
                                   ' ' + scraped_courses[i].title + '\n\n')
                    i += 1
                    issue_ct += 1
                    continue
                # If DB course is missing from scrape, log and iterate past
                else:
                    logger.warning("STALE COURSE: " +
                                   str(db_courses[j]['course_number']) +
                                   ' ' + db_courses[j]['title'] + '\n\n')
                    j += 1
                    issue_ct += 1
                    continue

            # Compare quarters/credits/titles, logging any differences
            for key in ['title', 'credits', 'qtrs']:
                if asdict(scraped_courses[i])[key] != db_courses[j][key]:
                    self._print_discrepancy(key, scraped_courses[i].course_number,
                                            db_courses[j][key], asdict(scraped_courses[i])[key])
                    issue_ct += 1

            # Build prereq list for this course from DB 
            db_prereqs = self._build_db_prereq_list(db_courses[j]['course_number'])

            # Compare prereqs, logging any differences
            if db_prereqs != scraped_courses[i].prereqs:
                self._print_discrepancy('prereq', scraped_courses[i].course_number,
                                        db_prereqs, scraped_courses[i].prereqs)
                issue_ct += 1

            # After comparisons, iterate forward in both course lists
            i += 1
            j += 1
        
        # Return number of issues found
        return issue_ct


    @staticmethod
    def _print_discrepancy(key: str, course: int, db_val: int | str | list,
                           scraped_val: int | str | list) -> None:
        """Writes details of any DB-scrape inconsistencies to stdout.

        Args:
            key: The field that has changed (e.g. 'title', 'credits', 'prereq')
            course: The course number of the course that has changed
            db_val: The value of the field in the DB
            scraped_val: The value of the field in the scraped JSON
        """
        logger.warning(str(course) + ' ' + " has changed " + str(key).upper() + '\n' +
                       "\tDB     : " + str(db_val) + '\n' +
                       "\tScraped: " + str(scraped_val) + '\n')
