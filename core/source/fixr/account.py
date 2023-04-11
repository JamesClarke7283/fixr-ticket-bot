from ...primitives.account import Account as BaseAccount
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Account(BaseAccount):
    def __init__(self, driver: webdriver, username: str, password: str):
        super().__init__(driver, username, password)

    def login(self):
        """Signs in the User in to the Fixr website."""
        # Visit the Login Page
        self.driver.get("https://fixr.co/login")

        # Wait for the login form to load
        wait = WebDriverWait(self.driver, 10)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'form')))

        # Find the login form
        login_form = self.driver.find_element(By.CSS_SELECTOR, 'form')

        # Fill in the login form
        login_form.find_element(By.CSS_SELECTOR, 'input#login-email').send_keys(self.username)
        login_form.find_element(By.CSS_SELECTOR, 'input#login-password').send_keys(self.password)

        # Submit the login form
        login_form.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

        # wait for redirect
        wait.until(EC.url_matches("https://fixr.co/"))

        # Wait for the user menu to load
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.cLEyZR')))