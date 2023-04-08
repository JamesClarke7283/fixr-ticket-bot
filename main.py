from selenium import webdriver
from core.events_book import post_event_data
from core.user_management import login


def main():
    # Replace this with the path to your webdriver (e.g., chromedriver)
    webdriver_path = "./chromedriver/chromedriver"

    # Initialize the webdriver with Chromium
    driver = webdriver.Chrome(executable_path=webdriver_path)

    # Make screen fullscreen
    driver.maximize_window()

    # Login to the website

    login(driver, 'james@james-clarke.ynh.fr', '7smrzVxzPuK6FPH')

    # Send POST request to server with link to image
    data = post_event_data(driver, "https://fixr.co/event/event-by-tester-gamer-tickets-789878529")

    # Print the response
    print(data)

    # Close the driver
    driver.quit()


if __name__ == "__main__":
    main()
