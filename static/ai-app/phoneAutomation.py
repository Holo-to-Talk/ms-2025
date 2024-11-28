from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from dotenv import load_dotenv
import os
import time

def phoneAutomation():
    load_dotenv()

    URL = os.getenv("URL")

    PHONE_NUMBER = os.getenv("PHONE_NUMBER")

    WEB_DRIVER_WAIT_TIME = 10

    TIME_SLEEP_TIME = 1

    options = Options()
    options.add_argument('--use-fake-ui-for-media-stream')
    options.add_argument('--headless')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-software-rasterizer')

    driver = webdriver.Chrome(options = options)

    driver.get(URL)

    startUpButton = WebDriverWait(driver, WEB_DRIVER_WAIT_TIME).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="startup-button"]'))
    )
    startUpButton.click()

    getDevicesButton = WebDriverWait(driver, WEB_DRIVER_WAIT_TIME).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="get-devices"]'))
    )
    getDevicesButton.click()

    phoneNumberInput = WebDriverWait(driver, WEB_DRIVER_WAIT_TIME).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="phone-number"]'))
    )
    phoneNumberInput.send_keys(PHONE_NUMBER)

    callButton = WebDriverWait(driver, WEB_DRIVER_WAIT_TIME).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="button-call"]'))
    )
    callButton.click()

    hangUpOutGoingButton = WebDriverWait(driver, WEB_DRIVER_WAIT_TIME).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="button-hangup-outgoing"]'))
    )

    while True:
        hangUpOutGoingButton_className = hangUpOutGoingButton.get_attribute('class')
        if 'hide' in hangUpOutGoingButton_className.split():
            driver.quit()
            break

        else:
            time.sleep(TIME_SLEEP_TIME)