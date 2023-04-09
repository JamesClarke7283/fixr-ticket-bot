from selenium import webdriver
from core.events_book import post_event_data
from core.user_management import login
from core.events_book import get_ticket_data
from selenium.webdriver.chrome.service import Service


def main():
    # Replace this with the path to your webdriver (e.g., chromedriver)
    webdriver_path = "./chromedriver/chromedriver"

    # Create a Service object with the executable path
    service = Service(executable_path=webdriver_path)

    # Initialize the WebDriver with the service object
    driver = webdriver.Chrome(service=service)

    # Make screen fullscreen
    driver.maximize_window()

    # Login to the website

    # login(driver, 'james@james-clarke.ynh.fr', '7smrzVxzPuK6FPH')

    login(driver, 'test@vivushub.com', 'testpass2023')
    # Send POST request to server with link to image
    data = post_event_data(driver, "https://fixr.co/event/event-by-tester-gamer-3-tickets-735680369")
    
    # Print the response
    print(data)

    # Close the driver
    driver.quit()


if __name__ == "__main__":
    main()
