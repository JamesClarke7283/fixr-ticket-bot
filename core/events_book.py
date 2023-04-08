from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import requests
from .utilities import select_elements_by_text, download_ticket, pdf_to_image, upload_image
from .events_info import get_event_data


def book_event(driver: webdriver, event_url, amount=1, is_free=True):
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
        if is_free:
            try:
                element = select_elements_by_text(driver, 'span', 'CONFIRM')
            except:
                element = select_elements_by_text(driver, 'span', 'CONFIRM')
                print("Couldn't find confirm button")
        else:
            try:
                element = select_elements_by_text(driver, 'span', 'CONTINUE')
            except:
                element = select_elements_by_text(driver, 'span', 'CONTINUE')
                print("Couldn't find continue button")
            # element = select_elements_by_text(driver, "span", "CONTINUE")[0].click()

    element[0].click()

    # Check if needs payment
    if not is_free:
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.XPATH, '//h3[contains(text(), "Payment")]')))

        # Click the pay button
        element = select_elements_by_text(driver, 'span', 'PAY NOW')[0].click()

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


def post_event_data(driver, event_url):
    # Get the event data
    event_data = get_event_data(driver, event_url)
    event_resell_data = event_data[0]
    print(event_resell_data)

    is_free = None
    if event_data[1] == "0":
        is_free = True
    else:
        is_free = False
    # Book and get the ticket url
    ticket_data = book_event_and_upload(driver, event_url, is_free=is_free)
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


def book_event_and_upload(driver, event_url, amount=1, is_free=True):
    # Book the first event
    ticket_data = book_event(driver, event_url, amount=amount, is_free=is_free)
    print(ticket_data)

    # Download the ticket
    file_path = Path(download_ticket(ticket_data["ticket_url"]))

    # Convert the ticket pdf to images
    pdf_to_image(file_path)

    # Upload the image to the server
    media_url = upload_image("images/page_1.png")
    return media_url, ticket_data
