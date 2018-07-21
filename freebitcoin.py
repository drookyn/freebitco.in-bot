import pickle
import os.path
import requests
import sched
import time
import logging
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from pyvirtualdisplay import Display
from random import randint
from fake_useragent import UserAgent
from raven import Client
from dotenv import load_dotenv
from pathlib import Path

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path, verbose=True)

class Log():
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        # create formatter
        formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')

        # create console handler
        consoleHandler = logging.StreamHandler()
        consoleHandler.setLevel(logging.DEBUG)
        consoleHandler.setFormatter(formatter)

        # create file handler
        fileHandler = logging.FileHandler('info.log')
        fileHandler.setLevel(logging.INFO)
        fileHandler.setFormatter(formatter)

        # add handler to logger
        self.logger.addHandler(consoleHandler)
        self.logger.addHandler(fileHandler)

class FreebitcoinBot():
    def __init__(self):
        self.log = Log()
        self.log.logger.info('initializing')
        self.base_url = 'https://freebitco.in/'
        self.useragent = UserAgent()

    def start_driver(self):
        self.log.logger.info('starting driver')
        self.display = Display(visible=0, size=(800, 600))
        self.display.start()
        self.profile = webdriver.FirefoxProfile()
        self.profile.set_preference(
            "general.useragent.override",
            self.useragent.random
        )
        options = Options()
        options.set_headless(headless=(os.getenv('HEADLESS') == 'True'))
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
        login_button = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, '//*[contains(@class, "login_menu_button")]//a'))
        )

        login_button.click()
        email_field = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, 'login_form_btc_address'))
        )
        password_field = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, 'login_form_password'))
        )

        email_field.send_keys(os.getenv('EMAIL'))
        password_field.send_keys(os.getenv('PASSWORD'))

        self.driver.find_element_by_id('login_button').click()
        self.log.logger.info('login success')

    def set_play_buttons(self):
        try:
            self.no_captcha_button = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(
                    (By.ID, 'play_without_captchas_button'))
            )
            self.play_button = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(
                    (By.ID, 'free_play_form_button'))
            )
        except:
            pass

    def dissmiss_consent(self):
        try:
            consent_button = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(
                    (By.XPATH, '//*[contains(@class, "cc_btn_accept_all")]'))
            )

            consent_button.click()
        except:
            pass

    def set_time_remaining(self):
        try:
            self.time_remaining = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.ID, 'time_remaining'))
            )
        except:
            pass

    def roll(self):
        self.log.logger.info('roll')
        try:
            self.set_play_buttons()
            self.no_captcha_button.click()
            self.play_button.click()

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


class Scheduler():
    def __init__(self):
        self.update_seconds = (60 * 60) + 30
        self.scheduler = sched.scheduler(time.time, time.sleep)

    def work(self, sc):
        self.bot = FreebitcoinBot()
        self.bot.work()
        self.scheduler.enter(self.update_seconds, 1, self.work, (sc,))

    def start(self):
        self.bot = FreebitcoinBot()
        self.bot.work()
        self.scheduler.enter(self.update_seconds, 1,
                             self.work, (self.scheduler,))
        self.scheduler.run()


def main():
    sentry_url = os.getenv('SENTRY_URL')

    if sentry_url:
        client = Client(sentry_url)

    try:
        scheduler = Scheduler()
        scheduler.start()
    except KeyboardInterrupt:
        sys.exit()
    except:
        if sentry_url:
            client.captureException()
        else:
            pass


if __name__ == "__main__":
    main()
