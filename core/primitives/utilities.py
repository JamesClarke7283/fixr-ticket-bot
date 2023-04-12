import urllib.request
from pdf2image import convert_from_path
import os
from datetime import datetime
import re
import logging

from __init__ import LOGLEVEL

logging.basicConfig(level=LOGLEVEL)


def download_ticket(ticket_url):
    # Download the ticket pdf
    os.makedirs("downloads", exist_ok=True)
    logging.debug(f"Downloading ticket from '{ticket_url}'")
    urllib.request.urlretrieve(ticket_url, "downloads/filename.pdf")
    return "downloads/filename.pdf"


def pdf_to_image(pdf_path, dpi=200):
    images = convert_from_path(pdf_path, dpi)
    os.makedirs("images", exist_ok=True)
    for i, image in enumerate(images):
        image_path = os.path.join("images", f"page_{i+1}.png")
        image.save(image_path, "PNG")

    logging.debug(f"Converted {len(images)} pages from '{pdf_path}' to images in 'images'")
    return image_path


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
