from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Replace this with the path to your webdriver (e.g., chromedriver)
webdriver_path = "./chromedriver/chromedriver"

# The URL to be scraped
url = "https://fixr.co/search?page=10&type=events&from=2023-04-05&lat=51.50740&lng=-0.11960"

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


login(driver)

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
    #event_price = event_card.find_element(By.CSS_SELECTOR, '.hnzhkD span').text

    event_data = {
        'title': event_title,
        'date': event_date,
        'location': event_location,
        #'price': event_price
    }

    events_data.append(event_data)

# Print the extracted data
for event in events_data:
    print(event)


# Close the driver
driver.quit()
