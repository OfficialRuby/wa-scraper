from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
import time
import sys
from utils.settings import CHROME_PROFILE, CHROME_DRIVER_PATH
WAIT_TIME = 10


class WAScrapper:
    def __init__(self) -> None:
        self.options = webdriver.ChromeOptions()
        self.options.add_argument(CHROME_PROFILE)
        self.service = Service(CHROME_DRIVER_PATH)
        self.driver = WebDriver(service=self.service, options=self.options)
        self.driver.get("https://web.whatsapp.com/")
        self.driver.maximize_window()
        try:
            with open('groups.txt', 'r') as f:
                self.group_names = f.readlines()
        except FileNotFoundError:
            print("groups.txt file missing, please create this file in the absolute path")
            sys.exit()

    def send_message(self, contact_name):
        pass

    def fetch_messages(self):
        input('Please click enter after loading completes: ')
        time.sleep(2)
        for group_name in self.group_names:
            group = self.driver.find_element(
                By.XPATH, f'//*[@title="{group_name.strip()}"]')
            group.click()
            WebDriverWait(self.driver, WAIT_TIME).until(
                EC.presence_of_element_located((By.CLASS_NAME, '_27K43')))
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")
            chats = self.driver.find_elements(By.CLASS_NAME, '_27K43')
            with open('chats.txt', 'a') as f:
                for chat in chats:
                    f.writelines(chat.text + '\n')
        time.sleep(10)
