import pickle
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from pyvirtualdisplay import Display
from random import randint
from fake_useragent import UserAgent
import os

class Bot():
    def __init__(self, log):
        self.log = log
        self.log.logger.info('initializing')
        self.base_url = 'https://freebitco.in/'
        self.useragent = UserAgent()

    def start_driver(self):
        self.log.logger.info('starting driver')
        self.display = Display(visible=0, size=(800, 600))
        self.display.start()
        # get random useragent
        self.profile = webdriver.FirefoxProfile()
        self.profile.set_preference(
            "general.useragent.override",
            self.useragent.random
        )
        # set headless
        options = Options()
        options.set_headless(headless=(os.getenv('HEADLESS') == 'True'))
        # start selenium driver
        self.driver = webdriver.Firefox(self.profile, firefox_options=options)
        self.driver.implicitly_wait(5)

    def close_driver(self):
        self.log.logger.info('closing driver')
        self.display.stop()
        self.driver.quit()

    def get_page(self, url):
        self.driver.get(url)

    def login(self):
        self.log.logger.info('login')
        # search login button
        login_button = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, '//*[contains(@class, "login_menu_button")]//a'))
        )

        # click login button
        login_button.click()

        # search email field
        email_field = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, 'login_form_btc_address'))
        )

        # search password field
        password_field = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, 'login_form_password'))
        )

        # insert email and password
        email_field.send_keys(os.getenv('EMAIL'))
        password_field.send_keys(os.getenv('PASSWORD'))

        # send login data
        self.driver.find_element_by_id('login_button').click()
        self.log.logger.info('login success')

    def set_play_buttons(self):
        try:
            # search no captcha button
            self.no_captcha_button = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(
                    (By.ID, 'play_without_captchas_button'))
            )

            # search play button
            self.play_button = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(
                    (By.ID, 'free_play_form_button'))
            )
        except:
            pass

    def dissmiss_consent(self):
        try:
            # search and click consent button
            consent_button = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(
                    (By.XPATH, '//*[contains(@class, "cc_btn_accept_all")]'))
            )

            consent_button.click()
        except:
            pass

    def set_time_remaining(self):
        try:
            # search time remaining
            self.time_remaining = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.ID, 'time_remaining'))
            )
        except:
            pass

    def roll(self):
        self.log.logger.info('roll')
        try:
            self.set_play_buttons()
            # click no captcha and roll button
            self.no_captcha_button.click()
            self.play_button.click()

            # search results
            self.role_result = WebDriverWait(self.driver, 60).until(
                EC.visibility_of_element_located((By.ID, 'winnings'))
            )
            self.log.logger.info('role success')
            self.log.logger.info('rolled {} BTC'.format(self.role_result.text))
        except:
            pass

    def notify(self):
        self.log.logger.info('notify')
        try:
            # notify via mercuriusbot.io
            secret = os.getenv('MERCURIUS_SECRET')
            if hasattr(self, 'role_result') and secret:
                res = requests.post(
                    'https://www.mercuriusbot.io/api/notify',
                    data={
                        'secret': secret,
                        'message': 'rolled {} BTC'.format(self.role_result.text)
                    }
                )

                if res.status_code != 200:
                    self.log.logger.error(res.text)
                else:
                    self.log.logger.info('notify success')
        except:
            pass

    def work(self):
        try:
            self.start_driver()
            self.get_page(self.base_url)
            self.set_play_buttons()

            if not hasattr(self, 'no_captcha_button') or not hasattr(self, 'play_button'):
                self.login()

            self.dissmiss_consent()
            self.set_time_remaining()

            if not hasattr(self, 'time_remaining') or not self.time_remaining:
                self.roll()
                self.notify()
            else:
                self.log.logger.info('already played')
        finally:
            self.close_driver()