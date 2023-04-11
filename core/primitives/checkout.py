from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException


class Checkout:
    def __init__(self, driver: webdriver, ticket):
        self.driver = driver
        self.ticket = ticket

