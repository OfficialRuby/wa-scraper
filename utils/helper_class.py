import re
from collections import OrderedDict, namedtuple
from selenium.webdriver.common.action_chains import ActionChains
import datetime
import base64
from selenium.common.exceptions import NoSuchElementException, NoSuchAttributeException
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
from utils.settings import CHROME_PROFILE, CHROME_DRIVER_PATH, XHR_SCRIPT, CLASSES_NAME
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
            if not os.path.isdir('images'):
                os.mkdir('images')

        except FileNotFoundError:
            print("groups.txt file missing, please create this file in the absolute path")
            sys.exit()

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
                # self.perform_scroll()
                time.sleep(2)
                # self.download_image()
                # self.get_sender_info()
                # self.perform_side_panel_scroll()
                time.sleep(1)
                self.get_focusable_list()
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

    def get_focusable_list(self):
        messages = self.driver.find_elements(By.CLASS_NAME, '_7GVCb')
        time.sleep(2)
        for message in messages:
            new_element = message.parent.find_element(By.CLASS_NAME, '_3FuDI')
            print(new_element.parent)
            # print(message.text)
            # print(message.tag_name)
            # print(message.parent)
            print(message.location)
            # print(message.size)
            # print(dir(message.parent.save_screenshot('new-images/' +
            #                                          str(datetime.datetime.now()) + '.png')))
            # new_elements = message.create_web_element(message.parent)
            # for element in new_elements:
            #     print(element.text)

    def perform_side_panel_scroll(self) -> None:
        side_pane = self.driver.find_element(By.CLASS_NAME, '_2A1R8')
        loc = side_pane.location
        x_loc = loc.get('x')
        y_loc = loc.get('y')
        print(x_loc, y_loc)
        # self.driver.scroll(x=x_loc, y=y_loc, delta_x=0,
        #                    delta_y=500, duration=1)
        ActionChains(self.driver).scroll(x=x_loc, y=y_loc, delta_x=1000,
                                         delta_y=0, duration=0).perform()
        # action_chains = ActionChains(self.driver)
        # action_chains.scroll(x: int, y: int, delta_x: int, delta_y: int, duration: int=0, origin: str='viewport').perform()

    def __get_chat_message(self, webelement) -> str:
        try:
            class_name = CLASSES_NAME.get('CHAT_MESSAGE')
            message_body = webelement.find_element(
                By.CSS_SELECTOR, class_name)
            return message_body.text
        except NoSuchElementException:
            pass

    def __get_chat_author(self, webelement) -> str:
        try:
            pattern = r"\b[A-Z][a-z]+ [A-Z][a-z]+\b"
            copyable_text = CLASSES_NAME.get('COPYABLE_TEXT')
            chat_class = webelement.find_element(
                By.CSS_SELECTOR, copyable_text)
            time_str = chat_class.get_attribute('data-pre-plain-text')
            if time_str:
                match = re.search(pattern, time_str)
                if match:
                    author = match.group()
                    return author

        except NoSuchElementException:
            # not all elements has sender info
            pass
        except NoSuchAttributeException:
            pass

    def __get_chat_timestamp(self, webelement) -> str:
        try:
            regex = r"\[(\d{1,2}:\d{2}), (\d{1,2}/\d{1,2}/\d{4})\]"
            copyable_text = CLASSES_NAME.get('COPYABLE_TEXT')
            chat_class = webelement.find_element(
                By.CSS_SELECTOR, copyable_text)
            time_str = chat_class.get_attribute('data-pre-plain-text')
            if time_str:
                match = re.search(regex, time_str)
                if match:
                    time = match.group(1)
                    date = match.group(2)
                    timestamp_str = date+" " + time
                    datetime_fmt = "%m/%d/%Y %H:%M"
                    timestamp = datetime.datetime.strptime(
                        timestamp_str, datetime_fmt)
                return timestamp

        except NoSuchElementException:
            # not all elements has sender info
            # TODO: refactor to use logging in production
            pass

    def __get_chat_id(self, webelement) -> str:
        try:
            data_id = CLASSES_NAME.get('DATA_ID')
            chat_id = webelement.get_attribute(data_id)
            return chat_id
        except NoSuchAttributeException:
            # TODO: refactor to use logging in production
            print(f'Error occured: unable to locate attribute with {data_id}')
            self.driver.quit()

    def __get_chat_image(self, webelement) -> str:
        try:
            selector = CLASSES_NAME.get('IMAGE_SELECTOR')
            image = webelement.find_elements(
                By.CSS_SELECTOR, selector)
            img_src = image[1].get_attribute('src')
            validator = Validator()
            validator.validate_link(img_src)
            if validator.is_valid:
                result = self.driver.execute_async_script(
                    XHR_SCRIPT, validator.validated_link)
                if type(result) == int:
                    raise Exception("Request failed with status %s" % result)
                final_image = base64.b64decode(result)
                image_path = f'images/{datetime.datetime.now()}.jpg'
                with open(image_path, 'wb') as f:
                    f.write(final_image)
                return image_path
            return 'Hello'
        except NoSuchElementException:
            # TODO: refactor to use logging in production
            print(
                f'Error occured: unable to locate class selector with the value {selector}')
            pass
        except IndexError:
            print('Image index out of range')
            pass

    def perform_test(self):
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
                    EC.presence_of_element_located((By.CLASS_NAME, CLASSES_NAME.get('CHAT_ROW'))))
                time.sleep(2)
                # self.__get_chat_image()
                # self.get_sender_info()
                # self.perform_side_panel_scroll()
                time.sleep(1)

                chats = self.driver.find_elements(
                    By.CLASS_NAME, CLASSES_NAME.get('CHAT_ROW'))
                for webelement in chats:
                    pass

                    # chat_id = self.__get_chat_id(webelement)
                    # chat_id = self.__get_chat_image(webelement)
                    # chat_id = self.__get_chat_timestamp(webelement)
                    # chat_id = self.__get_chat_author(webelement)
                    # chat_id = self.__get_chat_message(webelement)
            except KeyError:
                print(f'Group with the name {group_name} could not be found')
                sys.exit()
        print('Completed')
        time.sleep(2)
        self.driver.quit()
