from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def login(driver: webdriver, username: str, password: str):
    """Logs in to the Fixr website."""
    # The URL to be scraped
    url = "https://fixr.co/login"
    driver.get(url)

    # Wait for the login form to load
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'form')))

    # Find the login form
    login_form = driver.find_element(By.CSS_SELECTOR, 'form')

    # Fill in the login form
    login_form.find_element(By.CSS_SELECTOR, 'input#login-email').send_keys(username)
    login_form.find_element(By.CSS_SELECTOR, 'input#login-password').send_keys(password)

    # Submit the login form
    login_form.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

    # wait for redirect
    wait = WebDriverWait(driver, 10)
    wait.until(EC.url_matches("https://fixr.co/"))

    # Wait for the user menu to load
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.cLEyZR')))
