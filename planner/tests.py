from django.test import LiveServerTestCase, Client
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import requests, datetime


class TestStaticAssets(LiveServerTestCase):
    @classmethod
    def setUp(cls):
        super().setUpClass()
        cls.client = Client()
        response = cls.client.get('/')
        cls.soup = BeautifulSoup(response.content, 'html.parser')
    
    # Banner image is served in stylesheet, sorry 4 hardcoding
    def test_homepage_banner(self):
        response = self.client.get('/static/planner/logo.png')
        self.assertEqual(response.status_code, 200)
    
    # Test all other links/static assets (a, link, script)
    def test_homepage_links(self):
        els = self.soup.select('a, link, script')
        urls = [el.get('src') or el.get('href') for el in els]
        for url in urls:
            # (linkedin will block requests from selenium)
            if not url or 'linkedin' in url:
                continue
            # test external urls
            elif url and url.startswith('http'):
                response = requests.get(url)
                self.assertEqual(response.status_code, 200, f'Failed to load {url}: {response.status_code}')
            # test static urls served by app
            else:
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200, f'Failed to load {url}: {response.status_code}')

class TestHomePageDemo(LiveServerTestCase):
    # currently just testing static page contents - might do separate class for drag and drop tests

    fixtures = ['latest-test-data.json']

    def setUp(self):
        self.browser = webdriver.Chrome()
        self.browser.get(self.live_server_url)
        self.browser.implicitly_wait(2) # implicit wait = "wait this long to give up on finding element"

        # get/store demo schedule contents

    def tearDown(self):
        self.browser.quit()
    
    # page title is correct
    def test_homepage_title(self):
        self.assertIn('C.A.S.T.O.R.', self.browser.title)

    # schedules list is empty
    def test_homepage_schedule_list_empty(self):
        schedules_list = self.browser.find_element(By.ID, 'schedules-list')
        self.assertEqual('', schedules_list.text)
    
    # schedule has correct quarters (all four of current year)
    def test_homepage_schedule_quarters(self):
        demo_qtrs = self.browser.find_elements(By.CLASS_NAME, 'qtr')
        qtr_vals = [qtr.get_attribute('data-qtr') for qtr in demo_qtrs]
        qtr_vals.sort()
        self.assertEqual(qtr_vals, ['0', '1', '2', '3'])
        for qtr in demo_qtrs:
            self.assertEqual(qtr.get_attribute('data-yr'), str(datetime.datetime.now().year))

