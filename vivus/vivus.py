from selenium import webdriver
from core.primitives.vivus_api import get_excluded_keywords, create_resell_event, get_ticket_budget, upload_media, filter_specific_dates
# event_list_resale_owned
from .broker import Broker, Source
from core.primitives.utilities import pdf_to_image, download_ticket
import json
import logging
from __init__ import LOGLEVEL

logging.basicConfig(level=LOGLEVEL)


class Vivus:
    def __init__(self, driver: webdriver, source: Source, lgusername: str, broker_site_username: str, broker_site_password: str, upload_password: str):
        self.driver = driver
        self.lgusername = lgusername
        self.broker_site_username = broker_site_username
        self.broker_site_password = broker_site_password
        self.source = source
        self.upload_password = upload_password

        self.broker = Broker(driver, source)

        # Login to the selected source
        self.broker_account = self.broker.account(driver, broker_site_username, broker_site_password)
        self.broker_account.login()

    def book_ticket(self, event_url: str):
        """Book a ticket for the event"""

        event = self.broker.event(self.driver, event_url)

        is_in_date = event.is_in_date()
        logging.info(f"Is in date:\t'{str(is_in_date)}'")

        is_bought = event.is_bought(self.lgusername)
        logging.info(f"Is bought:\t'{str(is_bought)}'")

        is_event_finished = event.is_event_finished()
        logging.debug(f"Is event finished:\t'{str(is_event_finished)}'")

        if not is_bought and is_in_date and not is_event_finished:
            self.driver.get(event_url)
            logging.debug(json.dumps(event.all_properties, indent=4))

            # Get excluded keywords
            excluded_keywords = get_excluded_keywords(event.organizer)
            budget = get_ticket_budget()

            # Get the ticket data
            ticket_list = self.broker.ticket_list(self.driver, event)
            # Filter the tickets by the excluded keywords
            ticket_list.tickets = ticket_list.filter_by_exclude_keywords(excluded_keywords)

            # Filter the tickets by the budget
            ticket_list.tickets = ticket_list.filter_by_budget(budget["maxBudget"], budget["minBudget"])
            logging.info(f"Filtered Tickets:\t{ticket_list.tickets}")

            ticket_checkout = None
            if len(ticket_list.tickets) > 0:
                bought_ticket = ticket_list.tickets[0]
                logging.info(f"Bought Ticket:\t'{bought_ticket.name}'")

                logging.info(f"Bought ticket element:\t'{bought_ticket.web_element.text}'")

                ticket_checkout = bought_ticket.buy(1)
                logging.info(f"Ticket Checkout:\t'{ticket_checkout}'")
                if ticket_checkout.is_insufficient_funds:
                    logging.error("Insufficient funds")
                    return None
                else:
                    # Get the ticket pdf
                    pdf_url = ticket_checkout.ticket_pdf_url
                    logging.info(f"PDF URL:\t'{pdf_url}'")

                    # Download the ticket pdf
                    pdf_path = download_ticket(pdf_url)
                    logging.info(f"PDF Path:\t'{pdf_path}'")

                    # Convert the pdf to an image
                    image_path = pdf_to_image(pdf_path)
                    logging.info(f"Image Path:\t'{image_path}'")

                    # Upload the image to the server
                    media_url = upload_media(image_path, self.upload_password)["mediaUrl"]
                    logging.info(f"Media URL:\t'{media_url}'")

                    # Create the event
                    ticket_data = [{"name": bought_ticket.name, "price": bought_ticket.price, "media": media_url}]
                    logging.info(f"Ticket Data:\t {ticket_data}")

                    data = create_resell_event("PublicVH", event.title, event.opens, event.closes, "N/A", "United Kingdom", self.source.value, ticket_data, event.poster_url)
                    logging.info(f"Resell Event Response:\t {data}")
                    return data
            else:
                if is_bought is None:
                    logging.warning(f"Ticket event: '{event.title}' query failed with error")
                if is_bought:
                    logging.warning(f"Ticket event: '{event.title}' already exists")
                if not is_in_date:
                    logging.warning(f"Event: '{event.title}' is not in date")
                if is_event_finished:
                    logging.warning(f"Event: '{event.title}' is finished")
                return None

    def book_tickets(self, driver: webdriver, event_list_page: str):
        """Book tickets for the events in the event list page"""
        event_list = self.broker.event_list(driver, event_list_page)
        event_urls = []
        for event in event_list.event_list:
            event_urls.append(event.url)

        for event_url in event_urls:
            self.book_ticket(event_url)
