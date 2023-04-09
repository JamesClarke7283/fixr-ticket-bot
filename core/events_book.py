from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import requests
from .utilities import select_elements_by_text, download_ticket, pdf_to_image, upload_image
from .events_info import get_event_data


def get_ticket_data(driver):

    wait = WebDriverWait(driver, 10)
    # wait for individual tickets to load
    wait.until(EC.presence_of_element_located((By.XPATH, '//div[h3[text()="Individual tickets"]]')))

    ticket_section = driver.find_element(By.XPATH, '//div[h3[text()="Individual tickets"]]')
    tickets = ticket_section.find_elements(By.CSS_SELECTOR, '.hrObei')
    tickets_data = []

    for ticket_element in tickets:
        ticket = ticket_element.text.split("\n")
        ticket_name = ticket[0]
        ticket_price = ticket[1].replace("£", "")
        tickets_data.append({'name': ticket_name, 'price': float(ticket_price)})
    return tickets_data


def get_tickets_inp_boxes(driver):
    # Filter the span elements based on their text content
    ticket_inputs = driver.find_elements(By.XPATH, '//input[@type="tel"]')
    return ticket_inputs


def book_event(driver: webdriver, event_url, amount=1, is_free=True, excluded_keywords=[]):
    if amount > 10:
        raise ValueError("You can only book 10 tickets at a time")

    driver.get(event_url + "/tickets")

    # Wait for the input box to load
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="tel"]')))

    all_tickets_data = get_ticket_data(driver)
    print(all_tickets_data)

    ticket_index_selected = None
    for index, ticket in enumerate(all_tickets_data):
        if ticket['name'] not in excluded_keywords:
            if ticket['price'] == 0:
                ticket_index_selected = index
                break
            elif ticket['price'] > 0 and ticket_index_selected is None:
                ticket_index_selected = index
            elif ticket['price'] < all_tickets_data[ticket_index_selected]["price"]:
                ticket_index_selected = index

    print(ticket_index_selected)

    # Find the input box
    print("get input boxes:")
    ticket_inp_boxes = get_tickets_inp_boxes(driver)
    print(ticket_inp_boxes)
    ticket_inp_boxes[ticket_index_selected].send_keys(str(amount))

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
        "ticket_name": all_tickets_data[ticket_index_selected]['name'],
        "ticket_price": all_tickets_data[ticket_index_selected]['price'],
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

    event_resell_data["tickData"].append({"name": ticket_data[1]["ticket_name"], "media": ticket_data[0], "price": ticket_data[1]["ticket_price"]})
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
