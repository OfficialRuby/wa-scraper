import os
CHROME_DRIVER_PATH = 'webdriver/chromedriver'
session_user = os.getlogin()
CHROME_PROFILE = f"user-data-dir=/home/{session_user}/.config/google-chrome/whatsapp_test"
# CHROME_PROFILE = f"user-data-dir=/home/{session_user}/.config/google-chrome/whatsapp_tests"
