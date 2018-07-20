import pickle
import os.path
import requests
import sched
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from pyvirtualdisplay import Display
from random import randint
from fake_useragent import UserAgent
from raven import Client
from dotenv import load_dotenv
from pathlib import Path

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path, verbose=True)

class FreebitcoinBot():
    def __init__(self):
        print('initializing...')
        self.base_url = 'https://freebitco.in/'
        self.useragent = UserAgent()

    def start_driver(self):
        print('starting driver...')
        self.display = Display(visible=0, size=(800, 600))
        self.display.start()
        self.profile = webdriver.FirefoxProfile()
        self.profile.set_preference(
            "general.useragent.override", self.useragent.random)
        self.driver = webdriver.Firefox(self.profile)

    def close_driver(self):
        print('closing driver...')
        self.display.stop()
        self.driver.quit()

    def get_page(self, url):
        self.driver.get(url)

    def login(self):
        print('login...')
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

    def save_cookies(self):
        pickle.dump(self.driver.get_cookies(), open(
            os.getenv('COOKIE_FILE'), 'wb'))

    def load_cookies(self):
        if os.path.isfile(os.getenv('COOKIE_FILE')):
            cookies = pickle.load(open(os.getenv('COOKIE_FILE'), 'rb'))
            try:
                for cookie in cookies:
                    self.driver.add_cookie(cookie)
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
        print('roll...')
        try:
            self.set_play_buttons()
            self.no_captcha_button.click()
            self.play_button.click()
            self.save_cookies()

            self.role_result = WebDriverWait(self.driver, 60).until(
                EC.visibility_of_element_located((By.ID, 'winnings'))
            )
            print('...won {} BTC'.format(self.role_result.text))
        except:
            pass

    def notify(self):
        print('notify...')
        try:
            secret = os.getenv('MERCURIUS_SECRET')
            if hasattr(self, 'role_result') and secret:
                res = requests.post(
                    'https://www.mercuriusbot.io/api/notify',
                    data={
                        'secret': secret,
                        'message': 'free bitcoin: {} BTC'.format(self.role_result.text)
                    }
                )

                if res.status_code == 400:
                    print(res.text)
        except:
            pass

    def work(self):
        try:
            self.start_driver()
            self.get_page(self.base_url)
            self.load_cookies()
            self.set_play_buttons()

            if not hasattr(self, 'no_captcha_button') or not hasattr(self, 'play_button'):
                self.login()

            self.dissmiss_consent()
            self.set_time_remaining()

            if not hasattr(self, 'time_remaining') or not self.time_remaining:
                self.roll()
                self.notify()
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
    except:
        if sentry_url:
            client.captureException()
        else:
            pass


if __name__ == "__main__":
    main()
