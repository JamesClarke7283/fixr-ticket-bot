from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Replace this with the path to your webdriver (e.g., chromedriver)
webdriver_path = "./chromedriver/chromedriver"

# Configure Chrome options to use Chromium
chrome_options = Options()
chrome_options.binary_location = "/home/impulse/.guix-profile/bin/chromium"

# Initialize the webdriver with Chromium
driver = webdriver.Chrome(executable_path=webdriver_path, options=chrome_options)


def login(driver):
    # The URL to be scraped
    url = "https://fixr.co/login"
    driver.get(url)

    # Wait for the login form to load
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'form')))

    # Find the login form
    login_form = driver.find_element(By.CSS_SELECTOR, 'form')

    # Fill in the login form
    login_form.find_element(By.CSS_SELECTOR, 'input#login-email').send_keys('james@james-clarke.ynh.fr')
    login_form.find_element(By.CSS_SELECTOR, 'input#login-password').send_keys('7smrzVxzPuK6FPH')

    # Submit the login form
    login_form.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

    # wait for redirect
    wait = WebDriverWait(driver, 10)
    wait.until(EC.url_matches("https://fixr.co/"))

    # Wait for the user menu to load
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.cLEyZR')))


def get_events_data(driver):
    url = "https://fixr.co/search?page=10&type=events"
    driver.get(url)

    # Wait for the data to load
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a.PWhcx')))

    # Find the event cards
    event_cards = driver.find_elements(By.CSS_SELECTOR, 'a.PWhcx')

    # Extract data from the event cards
    events_data = []
    for event_card in event_cards:
        event_title = event_card.find_element(By.CSS_SELECTOR, '.kicvUg span').text
        event_date = event_card.find_element(By.CSS_SELECTOR, '.kWawed span').text
        event_locations = event_card.find_elements(By.CSS_SELECTOR, '.iNmIef span')
        event_location = ', '.join([event_location.text for event_location in event_locations])
        event_price = event_card.find_element(By.CSS_SELECTOR, '.sc-a0e7c443-7 span').text
        event_url = event_card.get_attribute('href')
        event_data = {
            'title': event_title,
            'date': event_date,
            'location': event_location,
            'price': event_price,
            'url': event_url
        }
        if event_title != "":
            events_data.append(event_data)

    return events_data


def select_elements_by_text(driver, selector, text):
    # Find all span elements on the page
    elements = driver.find_elements(By.CSS_SELECTOR, selector)

    # Filter the span elements based on their text content
    elements = [element for element in elements if element.text == text]
    return elements


def book_event(driver, event_url, amount=1):
    if amount > 10:
        raise ValueError("You can only book 10 tickets at a time")

    driver.get(event_url + "/tickets")

    # Wait for the input box to load
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="tel"]')))

    # Find the input box
    driver.find_element(By.CSS_SELECTOR, 'input[type="tel"]').send_keys(str(amount))

    # wait 2 seconds
    driver.implicitly_wait(2)

    # Filter the span elements based on their text content
    reserve_spans = select_elements_by_text(driver, 'span', 'Reserve')

    # Click the first span element that contains the text "Reserve"
    reserve_spans[0].click()

    # Wait for the opt out of communications box to load
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.ID, '21910-radio-no')))

    # Opt out of the communications
    driver.find_element(By.ID, '21910-radio-no').click()

    select_elements_by_text(driver, 'span', 'CONFIRM')[0].click()

    # Wait for view tickets button to appear
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.kBclag')))

    # Click the view tickets button
    select_elements_by_text(driver, 'span', 'View tickets')[0].click()

    # Wait for the tickets to load
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.sc-86ac4539-1 > a:nth-child(4)')))

    # Return the ticket pdf url
    ticket_url = driver.find_element(By.CSS_SELECTOR, '.sc-86ac4539-1 > a:nth-child(4)').get_attribute('href')
    # Wait 10 seconds
    driver.implicitly_wait(10)

    return ticket_url


# Login to the website
login(driver)
"""
# Get the events data
events_data = get_events_data(driver)

# Print the extracted data
for event in events_data:
    print(event)
"""


# Book the first event
ticket_url = book_event(driver, "https://fixr.co/event/mr-whites-at-night-by-marco-pierre-white-leicester-tickets-95333642")
print(ticket_url)


# Close the driver
driver.quit()
