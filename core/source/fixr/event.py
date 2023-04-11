from ...primitives.event import Event as BaseEvent
from ...primitives.event import EventList as BaseEventList
from ...source.fixr.event import Event_From_JSON
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from ...primitives.utilities import convert_date_string
import time 
from datetime import datetime
from ...primitives.vivus_api import event_list_resale_owned, filter_specific_dates
import json


@DeprecationWarning
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
        self.__organizer = driver.find_element(By.XPATH, '//h3[text()="Organised by"]/following-sibling::div//a').text
        self.__poster_url = driver.find_element(By.XPATH, f'//img[@alt="{self.title}"]').get_attribute("src")
        self.__price_from_raw = event_price
        self.__price_from = float(self.price_from_raw.replace("Tickets from ", "").replace("£", ""))
        self.__description = driver.find_element(By.XPATH, '//div[h3[contains(text(), "About")]]').text
        try:
            self.__opens = convert_date_string(driver.find_element(By.XPATH, '//span[contains(text(), "Opens")]').text)
        except:

            self.__opens = time.strftime("%d/%m/%Y, %H:%M:%S", time.gmtime(time.mktime((datetime.now().year, 12, 1, 0, 0, 0, 0, 0, 0))))

        try:
            self.__last_entry = convert_date_string(driver.find_element(By.XPATH, '//span[contains(text(), "Last entry")]').text)
        except:
            self.__last_entry = time.strftime("%d/%m/%Y, %H:%M:%S", time.gmtime(time.mktime((datetime.now().year, 12, 1, 0, 0, 0, 0, 0, 0))))

        try:
            self.__closes = convert_date_string(driver.find_element(By.XPATH, '//span[contains(text(), "Closes")]').text)
        except:
            self.__closes = time.strftime("%d/%m/%Y, %H:%M:%S", time.gmtime(time.mktime((datetime.now().year, 12, 1, 0, 0, 0, 0, 0, 0))))

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

    def is_bought(self, lgusername: str):
        bought_tickets = event_list_resale_owned(lgusername, self.title)
        if bought_tickets == []:
            return False
        else:
            return True

    def is_in_date(self):
        result = filter_specific_dates(self.organizer)
        if result == []:
            return False
        elif result == 'error':
            return True
        else:
            formatted_date = self.opens.split(",")[0].replace("/", "-")
            if formatted_date in result:
                return True
            return False

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


class Event_From_JSON(BaseEvent):
    def __init__(self, driver, event_url):
        super().__init__(driver, event_url)

        json_element = driver.find_element(By.XPATH, '//script[@id="__NEXT_DATA__" and @type="application/json"]')
        data = json.loads(json_element.get_attribute("innerHTML"))

        self.__title = data["props"]["pageProps"]["meta"]["name"]
        self.__organizer = data["props"]["pageProps"]["meta"]["salesAccount"]["name"]
        self.__poster_url = data["props"]["pageProps"]["meta"]["eventImages"][0]
        self.__price_from = data["props"]["pageProps"]["meta"]["cheapestTicket"]["price"]
        self.__description = driver.find_element(By.XPATH, '//div[h3[contains(text(), "About")]]').text
        input_format = "%Y-%m-%dT%H:%M:%S%z"
        output_format = "%d/%m/%Y, %H:%M"

        try:
            dt = datetime.strptime(data["props"]["pageProps"]["meta"]["openTimeVenueLocalised"], input_format)
            self.__opens = dt.strftime(output_format)
        except:
            self.__opens = time.strftime("%d/%m/%Y, %H:%M:%S", time.gmtime(time.mktime((datetime.now().year, 12, 1, 0, 0, 0, 0, 0, 0))))

        try:
            self.__last_entry = convert_date_string(driver.find_element(By.XPATH, '//span[contains(text(), "Last entry")]').text)
        except:
            self.__last_entry = time.strftime("%d/%m/%Y, %H:%M:%S", time.gmtime(time.mktime((datetime.now().year, 12, 1, 0, 0, 0, 0, 0, 0))))

        try:
            dt = datetime.strptime(data["props"]["pageProps"]["meta"]["closeTimeVenueLocalised"], input_format)
            self.__closes = dt.strftime(output_format)
        except:
            self.__closes = time.strftime("%d/%m/%Y, %H:%M:%S", time.gmtime(time.mktime((datetime.now().year, 12, 1, 0, 0, 0, 0, 0, 0))))
    
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

    def is_bought(self, lgusername: str):
        bought_tickets = event_list_resale_owned(lgusername, self.title)
        if bought_tickets == []:
            return False
        else:
            return True

    @property
    def all_properties(self):
        """Returns a dictionary of all the properties"""
        return {
            "title": self.title,
            "organizer": self.organizer,
            "poster_url": self.poster_url,
            "price_from": self.price_from,
            "description": self.description,
            "opens": self.opens,
            "last_entry": self.last_entry,
            "closes": self.closes}


class EventList(BaseEventList):
    def __init__(self, driver, event_list_url):
        super().__init__(driver, event_list_url)

        self.__event_list = []

        self.__event_list_url = event_list_url

        self.__event_list = self.__get_event_list()

    def __get_event_list(self):
        event_list = []
        event_list_elements = self.driver.find_elements(By.XPATH, '//div[@class="jckbTc"]/a')
        for event_element in event_list_elements:
            try:
                event_list.append(Event_From_JSON(self.driver, event_element.get_attribute("href")))
            except:
                pass
        return event_list

    @property
    def event_list(self):
        """Returns a list of Event objects"""
        return self.__event_list

    def get_event_by_date(self, date: str):
        """Returns a list of Event objects by the date of the event"""
        event_list = []
        for event in self.event_list:
            if event.opens.split(",")[0].replace("/", "-") == date:
                event_list.append(event)
        return event_list
