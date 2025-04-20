from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

class ScheduleJavaScriptTest(LiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.browser = webdriver.Chrome()  # or Firefox() if using GeckoDriver
        cls.browser.implicitly_wait(3)

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super().tearDownClass()

    def test_add_slot_and_detect_overlap(self):
        self.browser.get(f'{self.live_server_url}/your-url-path/')  # update with actual path

        # Click on the "Add Slot" button
        add_buttons = self.browser.find_elements(By.CLASS_NAME, 'add-slot')
        add_buttons[0].click()  # Click the first day's add button

        # Find the newly added time inputs
        start_input = self.browser.find_elements(By.NAME, lambda name: "start" in name)[-1]
        end_input = self.browser.find_elements(By.NAME, lambda name: "end" in name)[-1]

        start_input.send_keys("10:00")
        end_input.send_keys("09:00")  # Set overlapping time intentionally

        # Submit the form
        form = self.browser.find_element(By.TAG_NAME, 'form')
        form.submit()

        # Wait a bit for JavaScript alert
        time.sleep(1)

        # Handle alert
        alert = self.browser.switch_to.alert
        self.assertIn("Overlapping time slots detected", alert.text)
        alert.accept()
