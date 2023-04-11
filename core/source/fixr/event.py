from ...primitives.event import Event as BaseEvent
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from ...primitives.utilities import convert_date_string

class Event(BaseEvent):
    def __init__(self, driver: webdriver, event_url: str):
        super().__init__(driver, event_url)

        # Wait for the full page to load
        wait = WebDriverWait(driver, 10)
        wait.until(EC.visibility_of_element_located((By.XPATH, '//span[contains(text(), "Tickets")]')))
        wait.until(EC.presence_of_element_located((By.XPATH, '//b[contains(text(), "Tickets from") or contains(text(), "From free")]')))

        # Get the event price
        event_price = ""
        element = driver.find_element(By.CSS_SELECTOR, '.sc-d5f38634-5 > div:nth-child(1) > b:nth-child(1)').text
        if element.lower() == "From Free".lower():
            event_price = "0"
        else:
            event_price = element

        self.__title = driver.find_element(By.XPATH, '//h1[@title]').text
        self.__organizer = driver.find_element(By.XPATH, '//div[h3[contains(text(), "Organised by")]]').text
        self.__poster_url = driver.find_element(By.XPATH, f'//img[@alt="{self.title}"]').get_attribute("src")
        self.__price_from_raw = event_price
        self.__price_from = float(self.price_from_raw.replace("Tickets from ", "").replace("£", ""))
        self.__description = driver.find_element(By.XPATH, '//div[h3[contains(text(), "About")]]').text
        try:
            self.__opens = convert_date_string(driver.find_element(By.XPATH, '//span[contains(text(), "Opens ")]').text)
        except:
            self.__opens = "N/A"

        try:
            self.__last_entry = convert_date_string(driver.find_element(By.XPATH, '//span[contains(text(), "Last entry ")]').text)
        except:
            self.__last_entry = "N/A"

        try:
            self.__closes = convert_date_string(driver.find_element(By.XPATH, '//span[contains(text(), "Closes ")]').text)
        except:
            self.__closes = "N/A"

    @property
    def title(self) -> str:
        """The name of the event"""
        return self.__title

    @property
    def organizer(self) -> str:
        """The name of the organizer of the event"""
        return self.__organizer

    @property
    def poster_url(self) -> str:
        """The media URL of the poster for the event"""
        return self.__poster_url

    @property
    def price_from_raw(self) -> str:
        """The raw price from string, contains the Tickets from and the £ symbol with the price"""
        return self.__price_from_raw

    @property
    def price_from(self) -> float:
        """The price from as a float, without the Tickets from and the £ symbol"""
        return self.__price_from

    @property
    def description(self) -> str:
        """Information about the event"""
        return self.__description

    @property
    def opens(self):
        return self.__opens

    @property
    def last_entry(self):
        return self.__last_entry

    @property
    def closes(self):
        return self.__closes

    @property
    def all_properties(self):
        """Returns a dictionary of all the properties"""
        return {
            "title": self.title,
            "organizer": self.organizer,
            "poster_url": self.poster_url,
            "price_from_raw": self.price_from_raw,
            "price_from": self.price_from,
            "description": self.description,
            "opens": self.opens,
            "last_entry": self.last_entry,
            "closes": self.closes
        }
