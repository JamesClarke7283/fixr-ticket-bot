from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from vivus.vivus import Vivus
from vivus.broker import Source
from core.primitives.vivus_api import upload_media, filter_specific_dates, get_ticket_budget
from core.source.fixr.event import Event, EventList
import logging
from os import environ as os_environ
from __init__ import LOGLEVEL

logging.basicConfig(level=LOGLEVEL)


def main():
    # Replace this with the path to your webdriver (e.g., chromedriver)
    webdriver_path = "./chromedriver/chromedriver"

    # Create a Service object with the executable path
    service = Service(executable_path=webdriver_path)

    # Initialize the WebDriver with the service object
    driver = webdriver.Chrome(service=service)

    # Make screen fullscreen
    driver.maximize_window()

    # vh = Vivus(driver, Source.FIXR, 'PublicVH', 'james@james-clarke.ynh.fr', '7smrzVxzPuK6FPH')
    vh = Vivus(driver, Source.FIXR, 'PublicVH', 'test@vivushub.com', 'testpass2023', 'testpass2023')

    # Book a ticket via the VIVUS HUB API
    #response_data = vh.book_ticket("https://fixr.co/event/event-by-tester-gamer-3-tickets-735680369")

    #logging.info(response_data)

    # Get an event list
    el = EventList(driver, "https://fixr.co/search?page=1&type=events")

    for event in el.event_list:
        print(event)

    # Close the driver
    driver.quit()


if __name__ == "__main__":
    main()
