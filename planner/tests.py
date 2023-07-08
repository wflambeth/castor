from django.test import LiveServerTestCase, Client
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import requests


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

class HomePageContentTest(LiveServerTestCase):
    # currently just testing static page contents - might do separate class for drag and drop tests

    def setUp(self):
        self.browser = webdriver.Chrome()
        self.browser.get(self.live_server_url)
        self.browser.implicitly_wait(2) # implicit wait = wait this long to give up on finding element

    def tearDown(self):
        self.browser.quit()
    
    # page title is correct
    def test_home_page_title(self):
        self.assertIn('C.A.S.T.O.R.', self.browser.title)

    # schedules list is empty
    def test_home_page_empty_schedule_list(self):
        schedules_list = self.browser.find_element(By.ID, 'schedules-list')
        self.assertEqual('', schedules_list.text)
    
