from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException


class Checkout:
    def __init__(self, driver: webdriver, ticket):
        self.driver = driver
        self.ticket = ticket


class FixrCheckout(Checkout):
    def __init__(self, driver: webdriver, ticket):
        super().__init__(driver, ticket)

        # Set the is_free attribute depending on if the price is 0
        is_free = ticket.price == 0

        # Wait for the opt out of communications box to load
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.XPATH, '//*[contains(@id, "radio-no")]')))

        # Opt out of the communications
        driver.find_element(By.XPATH, '//*[contains(@id, "radio-no")]').click()

        # Click the continue button or confirm button depending on if the ticket is free
        if is_free:
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.XPATH, '//button[.//span[contains(text(), "CONFIRM")]]')))
            element = driver.find_element(By.XPATH, '//button[.//span[contains(text(), "CONFIRM")]]')
        else:
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.XPATH, '//button[.//span[contains(text(), "Continue")]]')))
            element = driver.find_element(By.XPATH, '//button[.//span[contains(text(), "Continue")]]')

        element.click()

        # Check if needs payment
        if not is_free:
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.XPATH, '//h3[contains(text(), "Payment")]')))

            # Click the pay button
            element = driver.find_element(By.XPATH, '//button[.//span[contains(text(), "PAY NOW")]]')
            element.click()

        # Wait for view tickets button to appear

        # Click the view tickets button
        element = None
        while element is None:
            try:
                element = driver.find_element(By.XPATH, '//button[.//span[contains(text(), "View tickets")]]')
            except NoSuchElementException:
                element = None
            if element is not None:
                try:
                    element.click()
                except ElementNotInteractableException:
                    element = None

        print("View tickets button clicked", element)

        # Wait for the tickets to load
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.sc-86ac4539-1 > a:nth-child(4)')))

        # Return the ticket pdf url
        self.ticket_pdf_url = driver.find_element(By.CSS_SELECTOR, '.sc-86ac4539-1 > a:nth-child(4)').get_attribute('href')
