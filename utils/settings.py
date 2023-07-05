import os
from utils.user_settings import *
WAIT_TIME = 10
SCROLL_COUNT = 4
MEDIA_DOWNLOAD_DELAY = 4
CHROME_DRIVER_PATH = 'webdriver/chromedriver'
GECKO_DRIVER_PATH = 'webdriver/geckodriver'
session_user = os.getlogin()
if USE_DEFAULT_PROFILE:
    CHROME_PROFILE = f"--user-data-dir=/home/{session_user}/.config/google-chrome/{DEFAULT_PROFILE_NAME}"
else:
    CHROME_PROFILE = f"--user-data-dir=/home/{session_user}/.config/google-chrome/whatsapp_test"

CHROME_USER = f"--profile-directory={DEFAULT_PROFILE_NAME}"

GECKO_PROFILE = f"/home/{session_user}/.mozilla/firefox/"
# GECKO_PROFILE = f"profiles/firefox/{session_user}.default"


CLASSES_NAME = {
    'FULL_CHAT': '_3nbHh',
    'CHAT_ROW': 'hY_ET',
    'CHAT_MESSAGE': 'span.selectable-text',
    'TIMESTAMP': 'cm280p3y',
    'SENDER_INFO': 'copyable-text',
    'IMAGE_SELECTOR': 'img.jciay5ix',
    'DATA_ID': 'data-id',
    'COPYABLE_TEXT': 'div.copyable-text',
    'UNSAVED_CONTACT': '_3FuDI',
}


XHR_SCRIPT = '''
var url = arguments[0];
var callback = arguments[1];
function toDataURL(url, callback) {
    var xhr = new XMLHttpRequest();
    xhr.onload = function () {
        var reader = new FileReader();
        reader.onloadend = function () {
            callback(reader.result);
        }
        reader.readAsDataURL(xhr.response);
    };
    xhr.open('GET', url);
    xhr.responseType = 'blob';
    xhr.send();
}

 toDataURL(url,  function (dataUrl) {
  callback(dataUrl);
  });
'''
