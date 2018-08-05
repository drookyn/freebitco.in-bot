from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

base_url = 'file:///E:/Downloads/freebitco.in-test/index.html'
driver = webdriver.Firefox()
driver.implicitly_wait(5)

driver.get(base_url)

consent_button = WebDriverWait(driver, 10).until(
  EC.visibility_of_element_located(
    (By.CLASS_NAME, 'cc_btn_accept_all')
  )
)

consent_button.click()
