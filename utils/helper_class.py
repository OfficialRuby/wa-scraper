from tqdm import tqdm
import dateparser
import pandas as pd
import re
from collections import namedtuple
from selenium.webdriver.common.action_chains import ActionChains
import datetime
import base64
from selenium.common.exceptions import NoSuchElementException, NoSuchAttributeException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as GeckoService

from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebDriver
from selenium.webdriver.firefox.webdriver import WebDriver as GeckoWebDriver
import time
import sys
import os
from utils.settings import *
from utils.validators import Validator, validate_b64_string


class WAScrapper:
    '''WhatsApp web scrapper class'''

    def __init__(self) -> None:
        '''Initialize module'''
        if BROWSER_TYPE == 'gecko':
            self.firefox_profile = webdriver.FirefoxProfile(GECKO_PROFILE)
            self.service = GeckoService(GECKO_DRIVER_PATH)
            self.driver = GeckoWebDriver(
                service=self.service, firefox_profile=self.firefox_profile)
        elif BROWSER_TYPE == 'chrome':
            self.options = webdriver.ChromeOptions()
            self.options.add_argument(CHROME_PROFILE)
            # self.options.add_argument(CHROME_USER)
            self.service = ChromeService(CHROME_DRIVER_PATH)
            self.driver = ChromeWebDriver(
                service=self.service, options=self.options)
        self.driver.get("https://web.whatsapp.com/")
        self.driver.maximize_window()
        self.SCROLL_COUNT = SCROLL_COUNT
        self.CSV_FILENAME = None
        self.DATE_FORMAT = DATE_FORMAT
        self.PHONE_REGEX = PHONE_REGEX
        self.NAME_REGEX = NAME_REGEX
        try:
            with open('groups.txt', 'r') as f:
                self.group_names = f.readlines()
            if not os.path.isdir('images'):
                os.mkdir('images')
            if not os.path.isdir('output'):
                os.mkdir('output')

        except FileNotFoundError:
            print("groups.txt file missing, please create this file in the absolute path")
            sys.exit()

    def __perform_scroll(self):
        '''perform scroll action'''
        chat_container = self.driver.find_element(
            By.XPATH, '//*[@data-testid="conversation-panel-messages"]')
        for _ in range(self.SCROLL_COUNT):
            chat_container.send_keys(Keys.CONTROL + Keys.HOME)
            # wait for chats to load
            time.sleep(2)

    def __get_chat_message(self, webelement) -> str:
        try:
            class_name = CLASSES_NAME.get('CHAT_MESSAGE')
            message_body = webelement.find_element(
                By.CSS_SELECTOR, class_name)
            return message_body.text
        except NoSuchElementException:
            # print("Chat element changed, chat not collected")
            pass

    def __get_chat_author(self, webelement) -> str:
        try:
            phone_pattern = self.PHONE_REGEX
            name_pattern = self.NAME_REGEX
            copyable_text = CLASSES_NAME.get('COPYABLE_TEXT')
            chat_class = webelement.find_element(
                By.CSS_SELECTOR, copyable_text)
            contact_str = chat_class.get_attribute('data-pre-plain-text')
            if contact_str:
                phone_match = re.search(phone_pattern, contact_str)
                name_match = re.search(name_pattern, contact_str)
                if phone_match:
                    author = phone_match.group()
                    return author
                # if contact is not in contact list
                elif name_match:
                    author = name_match.group(1)
                    return author
                else:
                    contact = CLASSES_NAME.get('UNSAVED_CONTACT')
                    author = webelement.find_element(
                        By.CLASS_NAME, contact)
                    if author:
                        return author.text

        except NoSuchElementException:
            # not all elements has sender info
            # print('No such elemment')
            pass
        except NoSuchAttributeException:
            pass

    def __get_chat_timestamp(self, webelement) -> str:
        try:
            regex1 = r"\[(\d{1,2}:\d{2}), (\d{1,2}/\d{1,2}/\d{4})\]"
            regex2 = r"\[(\d{1,2}:\d{2} [aApP][mM]), (\d{1,2}/\d{1,2}/\d{4})\]"
            copyable_text = CLASSES_NAME.get('COPYABLE_TEXT')
            chat_class = webelement.find_element(
                By.CSS_SELECTOR, copyable_text)
            time_str = chat_class.get_attribute('data-pre-plain-text')
            if time_str:
                match1 = re.search(regex1, time_str)
                match2 = re.search(regex2, time_str)
                if match1:
                    time_str = match1.group(1)
                    date_str = match1.group(2)
                    datetime_str = date_str+" " + time_str
                    datetime_fmt = self.DATE_FORMAT
                    try:
                        timestamp = datetime.datetime.strptime(
                            datetime_str, datetime_fmt)
                        return timestamp
                    except ValueError:
                        timestamp = dateparser.parse(datetime_str)
                        return timestamp
                elif match2:
                    time_str = match2.group(1)
                    date_str = match2.group(2)
                    datetime_str = date_str + " " + time_str
                    datetime_fmt = self.DATE_FORMAT
                    try:
                        timestamp = datetime.datetime.strptime(
                            datetime_str, datetime_fmt)
                        return timestamp
                    except ValueError:
                        timestamp = dateparser.parse(datetime_str)
                        return timestamp

            return

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
            # self.driver.quit()
            pass

    def __get_chat_image(self, webelement) -> str:
        try:
            selector = CLASSES_NAME.get('IMAGE_SELECTOR')
            image = webelement.find_elements(By.CSS_SELECTOR, selector)
            if image:
                main_image = image[1]
                img_src = main_image.get_attribute('src')
                validator = Validator()
                validator.validate_link(img_src)
                if validator.is_valid:

                    result = self.driver.execute_async_script(
                        XHR_SCRIPT, validator.validated_link)

                    if type(result) == int:
                        raise Exception(f"Request failed with status {result}")
                    base64_str = validate_b64_string(result)
                    final_image = base64.b64decode(base64_str)
                    validate_b64_string(result)
                    image_path = f'images/{datetime.datetime.now()}.jpg'
                    with open(image_path, 'wb') as f:
                        f.write(final_image)
                    return image_path
            return
        except NoSuchElementException:
            # TODO: refactor to use logging in production
            print(
                f'Error occured: unable to locate class selector with the value {selector}')
            pass
        except IndexError:
            # print('Image index out of range')
            pass

    def collect_chats(self):
        '''collect chat history'''
        try:
            input('Please click enter after loading completes: ')
            time.sleep(2)
            chat_history = []
            for group_name in self.group_names:
                try:

                    group = self.driver.find_element(
                        By.XPATH, f'//*[@title="{group_name.strip()}"]')
                    group.click()
                    chat_row = CLASSES_NAME.get('CHAT_ROW')
                    # wait until chat are loaded
                    WebDriverWait(self.driver, WAIT_TIME).until(
                        EC.presence_of_element_located((By.CLASS_NAME, chat_row)))
                    time.sleep(2)
                    self.__perform_scroll()
                    time.sleep(1)
                    chats = self.driver.find_elements(
                        By.CLASS_NAME, chat_row)
                    if chats:
                        for webelement in tqdm(chats, ascii=True, desc='Collecting chats'):
                            chat = self.get_message_data(webelement)
                            chat_history.append(chat)
                    else:
                        raise Exception(
                            f'Error: {chat_row} is not a valid class bame')

                except NoSuchElementException:
                    print(
                        f'Group with the name {group_name} could not be found')
                    pass
            print('Completed')
            time.sleep(2)
            # self.driver.close()
            self.driver.quit()
            return chat_history
        except KeyboardInterrupt:
            print("\n Process terminated by user")
            self.driver.quit()
            sys.exit()

    def get_message_data(self, webelement):
        '''collect message info for messages in chat history'''
        self.__load_chat_media(webelement)
        message_id = self.__get_chat_id(webelement)
        message_image = self.__get_chat_image(webelement)
        timestamp = self.__get_chat_timestamp(webelement)
        author = self.__get_chat_author(webelement)
        text = self.__get_chat_message(webelement)
        ChatMessage = namedtuple(
            'ChatMessage', ['message_id', 'message_image', 'timestamp', 'author', 'text'])
        message = ChatMessage._make(
            [message_id, message_image, timestamp, author, text])
        return message

    def export_chat_to_csv(self):
        if self.CSV_FILENAME:
            file_name = self.CSV_FILENAME
        else:
            file_name = f'output/{datetime.datetime.now()}.csv'
        chats = self.collect_chats()
        dataframe = pd.DataFrame(chats)
        return dataframe.to_csv(file_name)

    def __load_chat_media(self, webelement):
        # check if media is downloadable
        try:
            download_btn = webelement.find_element(
                By.XPATH, '//span[@data-testid="media-download"]')
            bool(download_btn)
            if download_btn:
                download_btn.click()
                time.sleep(MEDIA_DOWNLOAD_DELAY)
        except NoSuchElementException:
            pass
