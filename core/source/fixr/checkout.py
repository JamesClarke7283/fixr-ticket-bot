from ...primitives.checkout import Checkout as BaseCheckout
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, TimeoutException
import logging
from __init__ import LOGLEVEL
import time
logging.basicConfig(level=LOGLEVEL)


class Checkout(BaseCheckout):
    def __init__(self, driver: webdriver, ticket):
        super().__init__(driver, ticket)

        # Set the is_free attribute depending on if the price is 0
        is_free = ticket.price == 0
        self.ticket_pdf_url = None

        # If ticket protection option shows up, click the no button
        try:
            wait = WebDriverWait(driver, 2)
            wait.until(EC.presence_of_element_located((By.XPATH, '//h3[contains(text(), "Ticket protection")]')))

            # Click the no button
            element = driver.find_element(By.ID, 'ticket-protection-no')
            element.click()
        except NoSuchElementException:
            logging.error(f"Ticket protection not found, for ticket '{ticket.name}'")
        except ElementNotInteractableException:
            logging.error(f"Ticket protection not interactable, for ticket '{ticket.name}'")
        except TimeoutException:
            logging.error(f"Ticket protection timeout, for ticket '{ticket.name}'")
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

        time.sleep(5)
        driver.implicitly_wait(5)
        # Check if needs payment
        if not is_free:
            wait = WebDriverWait(driver, 10)
            wait.until(EC.visibility_of_element_located((By.XPATH, '//button[.//span[contains(text(), "PAY NOW")]]')))

            # Click the pay button
            element = driver.find_element(By.XPATH, '//button[.//span[contains(text(), "PAY NOW")]]')
            element.click()
        
        # Wait for the payment to complete
        # Is insufficient funds
        self.is_insufficient_funds = False
        try:
            wait = WebDriverWait(driver, 10)
            wait.until(EC.visibility_of_element_located((By.XPATH, '//div[contains(text(), "Your card has insufficient funds.")]')))
            self.is_insufficient_funds = True
        except:
            self.is_insufficient_funds = False

        # Wait for view tickets button to appear
        if not self.is_insufficient_funds:
            # Click the view tickets button
            element = None
            count = 0
            """
            while element is None and count < 5:
                try:
            """
            wait = WebDriverWait(driver, 15)
            try:
                wait.until(EC.visibility_of_element_located((By.XPATH, '//button[.//span[contains(text(), "View tickets")]]')))
            except TimeoutException:
                element = None
                wait.until(EC.presence_of_element_located((By.XPATH, '//button[.//span[contains(text(), "CANCEL")]]')))
                driver.find_element(By.XPATH, '//button[.//span[contains(text(), "CANCEL")]]').click()  
                # wait for alert to appear
                try:
                    wait.until(EC.alert_is_present())
                    driver.switch_to.alert.accept()
                except:
                    pass
            try:
                element = driver.find_element(By.XPATH, '//button[.//span[contains(text(), "View tickets")]]')
                element.click()
            except NoSuchElementException:
                element = None
            except TimeoutException:
                element = None
            
            """
                except NoSuchElementException:
                    element = None
                    driver.implicitly_wait(1)
                    count += 1
                if element is not None:
                    try:
                        element.click()
                    except ElementNotInteractableException:
                        element = None
            """
            if element is not None:
                logging.debug("View tickets button clicked", element)

                # Wait for the tickets to load
                wait = WebDriverWait(driver, 10)
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.sc-86ac4539-1 > a:nth-child(4)')))

                # Return the ticket pdf url
                self.ticket_pdf_url = driver.find_element(By.CSS_SELECTOR, '.sc-86ac4539-1 > a:nth-child(4)').get_attribute('href')
