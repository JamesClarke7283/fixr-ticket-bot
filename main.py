from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from vivus.vivus import Vivus
from vivus.broker import Source
from core.primitives.vivus_api import upload_media

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
    response_data = vh.book_ticket("https://fixr.co/event/dirt-tickets-288395502")

    print(response_data)


    # Close the driver
    driver.quit()


if __name__ == "__main__":
    main()
