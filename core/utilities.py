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


def select_elements_by_text(driver: webdriver, selector, text):
    # Find all span elements on the page
    elements = driver.find_elements(By.CSS_SELECTOR, selector)

    # Filter the span elements based on their text content
    elements = [element for element in elements if element.text == text]
    return elements


def select_elements_by_text_contains(driver: webdriver, selector, text):
    # Find all span elements on the page
    elements = driver.find_elements(By.CSS_SELECTOR, selector)

    # Filter the span elements based on their text content
    elements = [element for element in elements if element.text.find(text)]
    return elements


def download_ticket(ticket_url):
    # Download the ticket pdf
    os.makedirs("downloads", exist_ok=True)
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


def convert_date_string(date_string):

    # Remove ordinal (i.e., 'th', 'st', 'nd', 'rd') from the input string
    input_date_str_cleaned = re.sub(r'(\d)(st|nd|rd|th)', r'\1', date_string)

    # Parse the input string
    input_date = datetime.strptime(input_date_str_cleaned[4::], "%d %b at %I:%M %p (BST)")
    # Set the year to the current year
    input_date = input_date.replace(year=datetime.now().year)

    # Format the parsed date-time object
    output_date_str = input_date.strftime("%d/%m/%Y, %H:%M")
    return output_date_str