# wa-scrapper
WhatsApp web scrapping using python and Selenium
## Description 
This is an automation tool for collecting chats from a specified WhatsApp chat user or group chat
## Setup and Installation
- Download the webdriver that matches the version of your web browser
- In the base directory of this project, create a directory with the name `webdriver` 
- Enter the contact or group name in the `group.txt` file in the base directory of the project.
- Copy the downloaded webdriver into the newly created **webdriver** directory
- Activate a virtual environment (DYOR) 
- Install requirements by running `pip install -r requirements.txt`

## Running the Project
Launch the script by running `python main.py`

## Known Issue
WhatsApp HTML tags changes over time, consider updating the values of the tags by using your browser's inspect tool.
