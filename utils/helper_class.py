
import datetime
import base64
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
import time
import sys
import os
from utils.settings import CHROME_PROFILE, CHROME_DRIVER_PATH, XHR_SCRIPT
from utils.validators import Validator
WAIT_TIME = 10
SCROLL_COUNT = 4


class WAScrapper:
    '''WhatsApp web scrapper class'''

    def __init__(self) -> None:
        '''Initialize module'''
        self.options = webdriver.ChromeOptions()
        self.options.add_argument(CHROME_PROFILE)
        self.service = Service(CHROME_DRIVER_PATH)
        self.driver = WebDriver(service=self.service, options=self.options)
        self.driver.get("https://web.whatsapp.com/")
        self.driver.maximize_window()
        self.SCROLL_COUNT = SCROLL_COUNT
        try:
            with open('groups.txt', 'r') as f:
                self.group_names = f.readlines()
            os.mkdir('images')

        except FileNotFoundError:
            print("groups.txt file missing, please create this file in the absolute path")
            sys.exit()
        except FileExistsError:
            pass

    def perform_scroll(self):
        '''perform scroll action'''
        chat_container = self.driver.find_element(
            By.XPATH, '//*[@data-testid="conversation-panel-messages"]')
        for _ in range(self.SCROLL_COUNT):
            chat_container.send_keys(Keys.CONTROL + Keys.HOME)
            # wait for chats to load
            time.sleep(2)

    def fetch_messages(self):
        '''collect chat history'''
        input('Please click enter after loading completes: ')
        time.sleep(2)
        for group_name in self.group_names:
            try:

                group = self.driver.find_element(
                    By.XPATH, f'//*[@title="{group_name.strip()}"]')
                group.click()
                # wait until chat are loaded
                WebDriverWait(self.driver, WAIT_TIME).until(
                    EC.presence_of_element_located((By.CLASS_NAME, '_3nbHh')))
                # perform a scroll event
                self.perform_scroll()
                time.sleep(2)
                # self.download_image()
                self.get_sender_info()
                chats = self.driver.find_elements(By.CLASS_NAME, '_3nbHh')
                images = self.driver.find_elements(
                    By.CSS_SELECTOR, 'img.jciay5ix')
                self.download_image(images)
                with open('chats.txt', 'a') as f:
                    for chat in chats:
                        f.writelines(chat.text + '\n\n\n')
            except NoSuchElementException:
                print(f'Group with the name {group_name} could not be found')
                sys.exit()
        print('Completed')
        time.sleep(2)
        self.driver.quit()

    def download_image(self, elements: list):
        for image in elements:
            img_src = image.get_attribute('src')
            validator = Validator()
            validator.validate_link(img_src)
            if validator.is_valid:
                result = self.driver.execute_async_script(
                    XHR_SCRIPT, validator.validated_link)
                if type(result) == int:
                    raise Exception("Request failed with status %s" % result)
                final_image = base64.b64decode(result)
                with open(f'images/{datetime.datetime.now()}.jpg', 'wb') as f:
                    f.write(final_image)

    def get_sender_info(self):
        senders = self.driver.find_elements(
            By.CSS_SELECTOR, 'div.copyable-text')
        for sender in senders:
            sender_info = sender.get_attribute('data-pre-plain-text')
            print(sender_info)
