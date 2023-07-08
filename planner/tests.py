from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import requests

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

    # page has valid favicon
    def test_home_page_has_favicon(self):
        # favicon element exists
        favicon = self.browser.find_element(By.CSS_SELECTOR, 'link[rel="shortcut icon"]')
        self.assertIsNotNone(favicon)

        # favicon url is valid
        fav_url = favicon.get_attribute('href')
        response = requests.get(fav_url)
        self.assertEqual(response.status_code, 200)


    # schedules list is empty
    def test_home_page_empty_schedule_list(self):
        schedules_list = self.browser.find_element(By.ID, 'schedules-list')
        self.assertEqual('', schedules_list.text)
    
