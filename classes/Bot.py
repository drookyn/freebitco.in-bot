import pickle
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
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

        # check for error
        error_field = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, 'reward_point_redeem_result_error'))
        )

        if error_field:
            self.log.logger.info('login failed')
            return False
        
        self.log.logger.info('login success')
        return True

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
            self.rolled_results = WebDriverWait(self.driver, 60).until(
                EC.visibility_of_element_located((By.ID, 'winnings'))
            )
            self.rolled_rp = WebDriverWait(self.driver, 60).until(
                EC.visibility_of_element_located((By.ID, 'fp_reward_points_won'))
            )
            self.log.logger.info('roll success')
            self.log.logger.info('rolled {} BTC and {} RP'.format(self.rolled_results.text, self.rolled_rp.text))
        except:
            pass

    def notify(self, message):
        self.log.logger.info('notify')
        try:
            # notify via mercuriusbot.io
            secret = os.getenv('MERCURIUS_SECRET')
            if secret:
                res = requests.post(
                    'https://www.mercuriusbot.io/api/notify',
                    data={
                        'secret': secret,
                        'message': message
                    }
                )

                if res.status_code != 200:
                    self.log.logger.error(res.text)
        except:
            pass

    def work(self):
        try:
            self.start_driver()
            self.get_page(self.base_url)

            logged_in = self.login()

            if logged_in:
                self.dissmiss_consent()
                self.set_time_remaining()

                if not hasattr(self, 'time_remaining') or not self.time_remaining:
                    self.roll()

                    if hasattr(self, 'rolled_results') and hasattr(self, 'rolled_rp'):
                        self.notify('freebitco.in: rolled {} BTC and {} RP'.format(self.rolled_results.text, self.rolled_rp.text))
                else:
                    self.log.logger.info('already played')
            else:
                self.log.logger.error('login failed')                
                self.notify('freebitco.in: login failed')
        finally:
            self.close_driver()
