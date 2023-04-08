from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import urllib.request
import json
from pdf2image import convert_from_path
import os
import requests
import pyperclip
from datetime import datetime
import re

# Replace this with the path to your webdriver (e.g., chromedriver)
webdriver_path = "./chromedriver/chromedriver"

# Initialize the webdriver with Chromium
driver = webdriver.Chrome(executable_path=webdriver_path)


def login(driver, username, password):
    # The URL to be scraped
    url = "https://fixr.co/login"
    driver.get(url)

    # Wait for the login form to load
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'form')))

    # Find the login form
    login_form = driver.find_element(By.CSS_SELECTOR, 'form')

    # Fill in the login form
    login_form.find_element(By.CSS_SELECTOR, 'input#login-email').send_keys(username)
    login_form.find_element(By.CSS_SELECTOR, 'input#login-password').send_keys(password)

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
        try:
            event_price = select_elements_by_text(event_card, 'span', 'Tickets from')[0].text.replace("Tickets from", "").replace("£", "")
        except:
            element = select_elements_by_text(event_card, 'span', 'Free')[0].text
            if element.lower() == "Free".lower():
                event_price = "0"

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
    wait.until(EC.presence_of_element_located((By.ID, '11327-radio-no')))

    # Opt out of the communications
    driver.find_element(By.XPATH, '//*[contains(@id, "radio-no")]').click()
    
    # element = select_elements_by_text(driver, 'span', 'CONFIRM')
    #try:
    element = []
    while len(element) < 1:
        try:
            element = select_elements_by_text(driver, 'span', 'CONFIRM')
        except:
            element = select_elements_by_text(driver, 'span', 'CONFIRM')
            print("Couldn't find confirm button")
            #element = select_elements_by_text(driver, "span", "CONTINUE")[0].click()

    element[0].click()

    # Wait for view tickets button to appear
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.fFfpEg span')))

    # Click the view tickets button
    elements = []
    while len(elements) < 1:
        elements = select_elements_by_text(driver, 'span', 'View tickets')

    elements[0].click()

    # Wait for the tickets to load
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.sc-86ac4539-1 > a:nth-child(4)')))

    # Return the ticket pdf url
    ticket_url = driver.find_element(By.CSS_SELECTOR, '.sc-86ac4539-1 > a:nth-child(4)').get_attribute('href')

    ticket_data = {
        "ticket_url": ticket_url,
        "event_name": driver.find_element(By.CSS_SELECTOR, '.fhMDRR h2 span').text,
    }

    return ticket_data


def download_ticket(ticket_url):
    # Download the ticket pdf
    print(f"Downloading ticket from '{ticket_url}'")
    urllib.request.urlretrieve(ticket_url, "downloads/filename.pdf")
    return "downloads/filename.pdf"


def pdf_to_image(pdf_path, dpi=200):
    images = convert_from_path(pdf_path, dpi)
    os.makedirs("images", exist_ok=True)
    for i, image in enumerate(images):
        image_path = os.path.join("images", f"page_{i+1}.png")
        image.save(image_path, "PNG")

    print(f"Converted {len(images)} pages from '{pdf_path}' to images in 'images'")
    return image_path


# Upload image to server with requests
def upload_image(image_path):
    file = {'file': open(image_path, 'rb')}
    r = requests.post("https://media.james-clarke.ynh.fr/", files=file)

    # Add get/ beteween the url and the unique id
    elements = r.text.strip("\n").split("/")
    elements.insert(3, "get")

    # Join the elements back together
    media_url = "/".join(elements)
    return media_url


def book_event_and_upload(driver, event_url, amount=1):
    # Book the first event
    ticket_data = book_event(driver, event_url, amount=amount)
    print(ticket_data)

    # Download the ticket
    file_path = Path(download_ticket(ticket_data["ticket_url"]))

    # Convert the ticket pdf to images
    pdf_to_image(file_path)

    # Upload the image to the server
    media_url = upload_image("images/page_1.png")
    return media_url, ticket_data


def convert_date_string(date_string):

    # Remove ordinal (i.e., 'th', 'st', 'nd', 'rd') from the input string
    input_date_str_cleaned = re.sub(r'(\d)(st|nd|rd|th)', r'\1', date_string)

    # Parse the input string
    input_date = datetime.strptime(input_date_str_cleaned[4::], "%d %b at %I:%M %p (BST)")
    # Set the year to the current year
    input_date = input_date.replace(year=datetime.now().year)

    # Format the parsed datetime object
    output_date_str = input_date.strftime("%d/%m/%Y, %H:%M")
    return output_date_str


def get_event_data(driver, event_url):
    driver.get(event_url)

    # Wait for the event title to load
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.sc-3f2220de-8')))

    lgusername = "PublicVH"

    # Get the event title
    event_name = driver.find_element(By.CSS_SELECTOR, '.sc-3f2220de-8').text

    # Wait for the event organizer to load
    driver.wait = WebDriverWait(driver, 10)
    driver.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.hexfOP')))

    # Get the event organizer
    event_organizer = driver.find_element(By.CSS_SELECTOR, '.sc-83caa70f-1 > a').text

    try:
        # Get the event start date
        event_start_date = driver.find_element(By.CSS_SELECTOR, '.cLJFrd > div:nth-child(1)').text.replace("Opens ", "")
        event_start_date = convert_date_string(event_start_date)

        # Get the event end date
        event_end_date = driver.find_element(By.CSS_SELECTOR, '.cLJFrd > div:nth-child(2)').text.replace("Last entry ", "")
        event_end_date = convert_date_string(event_end_date)
    except:
        event_start_date = "N/A"
        event_end_date = "N/A"
    
    country = "United Kingdom"

    # Get the event location
    try:
        driver.find_element(By.CSS_SELECTOR, '.cFXLI').click()
        # get from clipboard
        event_location = pyperclip.paste()
    except:
        event_location = "N/A"

    try:
        event_price = select_elements_by_text(driver, "b", "Tickets from")[0].text
    except:
        element = select_elements_by_text(driver, "b", "From free")[0].text
        if element.lower() == "From Free".lower():
            event_price = "0"


    # Put in a dictionary
    event_data = {
        "lgusername": lgusername,
        "data": {
            "eventname": event_name,
            # "event_organizer": event_organizer,
            "eventstime": event_start_date,
            "eventetime": event_end_date,
            "eventlocation": event_location,
            "eventcountry": country,
            "purchaseSource": "Fixr",
            "rType": "create",
        }
        
    }
    return event_data, event_price


def post_event_data(driver, event_url):
    # Get the event data
    event_data = get_event_data(driver, event_url)
    event_resell_data = event_data[0]
    print(event_resell_data)

    # Book and get the ticket url
    ticket_data = book_event_and_upload(driver, event_url)
    print(ticket_data)

    event_resell_data["tickData"] = []

    event_resell_data["tickData"].append({"name": event_resell_data["data"]["eventname"], "media": ticket_data[0], "price": event_data[1]})
    print("Event resell data sent to VivusHub:")
    print(json.dumps(indent=4, obj=event_resell_data))
    print()

    # Send a POST request to the server with the event data
    r = requests.post("https://api.vivushub.com/createResell", json=event_resell_data)
    print("VivusHub response:", end="\n\n")
    print(r.text)
    return r.text


# Make screen fullscreen
driver.maximize_window()

# Login to the website

login(driver, 'james@james-clarke.ynh.fr', '7smrzVxzPuK6FPH')

"""
# Get the events data
events_data = get_events_data(driver)

# Print the extracted data
for event in events_data:
    print(event)
"""





# Send POST request to server with link to image
data = post_event_data(driver, "https://fixr.co/event/event-by-tester-gamer-tickets-789878529")

# Print the response
print(data)

# Get the event data
#event_data = get_event_data(driver, "https://fixr.co/event/mr-whites-at-night-by-marco-pierre-white-leicester-tickets-176201491")
#print(event_data)

# Close the driver
driver.quit()
