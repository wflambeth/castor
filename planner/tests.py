from django.test import TestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains

class HomePageContentTest(StaticLiveServerTestCase):
    # currently just testing static page contents - might do separate class for drag and drop tests

    def setUp(self):
        self.browser = webdriver.Chrome()
        # self.browser.implicitly_wait(3)
        # self.action_chains = ActionChains(self.browser)

    def tearDown(self):
        self.browser.quit()
    
    def test_home_page_title(self):
        self.browser.get(self.live_server_url)
        self.assertIn('C.A.S.T.O.R.', self.browser.title)
