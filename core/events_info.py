from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import urllib.request
import json
from pdf2image import convert_from_path
import os
import requests
import pyperclip
from datetime import datetime
import re

from .utilities import select_elements_by_text, convert_date_string, select_elements_by_text_contains


def get_events_data(driver: webdriver, pages=10):
    """Gets x pages worth of event data from the search page"""
    url = f"https://fixr.co/search?page={str(pages)}&type=events"
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


def get_event_data(driver, event_url):
    """Get the event data from the event page"""
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

    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.XPATH, '//b[contains(text(), "Tickets from") or contains(text(), "From free")]')))

    # Get the event price
    event_price = ""
    try:
        event_price = driver.find_element(By.XPATH, '//b[contains(text(), "Tickets from")]').text
        print("Event Price:\t", event_price)
    except:
        element = driver.find_element(By.XPATH, '//b[contains(text(), "From free")]').text
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
