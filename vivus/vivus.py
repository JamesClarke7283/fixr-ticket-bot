from selenium import webdriver
from core.primitives.vivus_api import get_excluded_keywords, create_resell_event, get_ticket_budget, upload_media
# event_list_resale_owned
from .broker import Broker, Source
from core.primitives.utilities import pdf_to_image, download_ticket
import json


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

        is_bought = event.is_bought(self.lgusername)
        print("Is bought\t", is_bought)
        if not is_bought:
            print(json.dumps(event.all_properties, indent=4))

            # Get excluded keywords
            excluded_keywords = get_excluded_keywords(event.organizer)
            budget = get_ticket_budget()

            # Get the ticket data
            ticket_list = self.broker._ticket_list(self.driver, event)
            # Filter the tickets by the excluded keywords
            ticket_list.tickets = ticket_list.filter_by_exclude_keywords(excluded_keywords)

            # Filter the tickets by the budget
            ticket_list.tickets = ticket_list.filter_by_budget(budget["maxBudget"], budget["minBudget"])

        
            ticket_checkout = None
            if len(ticket_list.tickets) > 0:
                bought_ticket = ticket_list.tickets[0]
                ticket_checkout = bought_ticket.buy(1)

                # Get the ticket pdf
                pdf_url = ticket_checkout.ticket_pdf_url

                # Download the ticket pdf
                pdf_path = download_ticket(pdf_url)

                # Convert the pdf to an image
                image_path = pdf_to_image(pdf_path)

                # Upload the image to the server
                media_url = upload_media(image_path, self.upload_password)["mediaUrl"]
                print(media_url)

                # Create the event
                ticket_data = [{"name": bought_ticket.name, "price": bought_ticket.price, "media": media_url}]
                data = create_resell_event("PublicVH", event.title, event.opens, event.closes, "N/A", "United Kingdom", self.source.value, ticket_data, event.poster_url)
                print(data)
            else:
                print("Ticket with this event already exists")
