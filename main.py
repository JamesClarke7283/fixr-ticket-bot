from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from vivus.vivus import Vivus
from vivus.broker import Source
from core.primitives.vivus_api import upload_media, filter_specific_dates
from core.source.fixr.event import Event_From_JSON


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
    response_data = vh.book_ticket("https://fixr.co/event/mr-whites-at-night-by-marco-pierre-white-leicester-tickets-689889932")

    print(response_data)
    #event = vh.broker.event(driver, "https://fixr.co/event/mr-whites-at-night-by-marco-pierre-white-leicester-tickets-689889932")
    #print(event.organizer)
    #dates = filter_specific_dates(event.organizer)

    #print(dates)
    # Close the driver
    driver.quit()


if __name__ == "__main__":
    main()
