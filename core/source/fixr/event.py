from ...primitives.event import Event as BaseEvent
from ...primitives.event import EventList as BaseEventList
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from ...primitives.utilities import convert_date_string
import time
from datetime import datetime
from ...primitives.vivus_api import event_list_resale_owned, filter_specific_dates
import json
import logging
from __init__ import LOGLEVEL
from selenium.common.exceptions import StaleElementReferenceException


logging.basicConfig(level=LOGLEVEL)


class Event(BaseEvent):
    def __init__(self, driver, event_url):
        super().__init__(driver, event_url)

        json_element = driver.find_element(By.XPATH, '//script[@id="__NEXT_DATA__" and @type="application/json"]')
        data = json.loads(json_element.get_attribute("innerHTML"))
        self.__url = event_url
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

    @property
    def url(self):
        return self.__url

    def is_bought(self, lgusername: str):
        """Checks if the user has bought tickets for this event"""
        try:
            bought_tickets = event_list_resale_owned(lgusername, self.title)
        except Exception:
            return None

        if bought_tickets == []:
            return False
        elif len(bought_tickets) > 0:
            if bought_tickets[0]["buyMore"] == "yes":
                return False
            else:
                return True
        else:
            return True

    def is_in_date(self):
        """Checks if the event is in the date range specified in API response"""
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

    def is_event_finished(self):
        """Checks if the event is finished"""
        if datetime.strptime(self.closes, "%d/%m/%Y, %H:%M") < datetime.now():
            return True
        return False

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
            "closes": self.closes,
            "url": self.url}

    def __repr__(self):
        return f"Event: {self.title} by {self.organizer}"


class EventList(BaseEventList):
    def __init__(self, driver, event_list_url):
        super().__init__(driver, event_list_url)

        self.__event_list = []

        self.__event_list_url = event_list_url

        self.__event_list = self.__get_event_list()

    def __get_event_list(self):
        event_list = []
        checkbox_hide_sold_out = self.driver.find_element(By.XPATH, '//label[text()="Hide sold out events"]/preceding-sibling::input[@type="checkbox"]')
        checkbox_hide_sold_out.click()
        self.driver.implicitly_wait(5)

        event_list_elements = self.driver.find_elements(By.XPATH, '//a[starts-with(@href, "/event/")]')

        logging.info(f"Found {len(event_list_elements)} events")
        event_urls = []

        for i in range(len(event_list_elements)):
            for _ in range(3):  # Retry up to 3 times
                try:
                    # Re-find the element by index
                    event_element = self.driver.find_elements(By.XPATH, '//a[starts-with(@href, "/event/")]')[i]
                    event_urls.append(event_element.get_attribute("href"))
                    break  # If successful, break out of the loop
                except StaleElementReferenceException:
                    logging.warning("StaleElementReferenceException encountered, retrying...")
                    time.sleep(1)  # Wait for a second before retrying
            else:
                logging.error("Failed to get event URL after multiple attempts")

        for event_url in event_urls:
            try:
                logging.info(event_url)
                event = Event(self.driver, event_url)
                logging.info(event)
                event_list.append(event)
            except:
                logging.error(f"Failed to get event at URL: {event_url}")

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
