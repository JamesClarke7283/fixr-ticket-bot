from selenium import webdriver
from core.events_book import post_event_data
from core.events_book import get_ticket_data, get_excluded_keywords
from selenium.webdriver.chrome.service import Service
from core.account import FixrAccount
from core.event import FixrEvent
from core.ticket import FixrTicketList
from core.utilities import pdf_to_image, upload_image, download_ticket
from core.vivus_api import get_excluded_keywords, create_resell_event, get_ticket_budget, event_list_resale_owned
import json


def main():
    # Replace this with the path to your webdriver (e.g., chromedriver)
    webdriver_path = "./chromedriver/chromedriver"

    # Create a Service object with the executable path
    service = Service(executable_path=webdriver_path)

    # Initialize the WebDriver with the service object
    driver = webdriver.Chrome(service=service)

    # Make screen fullscreen
    driver.maximize_window()

    # Login to the website

    # account = FixrAccount(driver, 'james@james-clarke.ynh.fr', '7smrzVxzPuK6FPH')
    account = FixrAccount(driver, 'test@vivushub.com', 'testpass2023')
    account.login()

    event = FixrEvent(driver, 'https://fixr.co/event/event-by-tester-gamer-tickets-789878529')
    print(json.dumps(event.all_properties, indent=4))
    
    # Get excluded keywords
    excluded_keywords = get_excluded_keywords(event.organizer)
    budget = get_ticket_budget()
    
    # Get the ticket data
    ticket_list = FixrTicketList(driver, event)
    # Filter the tickets by the excluded keywords
    ticket_list.tickets = ticket_list.filter_by_exclude_keywords(excluded_keywords)
    
    # Filter the tickets by the budget
    ticket_list.tickets = ticket_list.filter_by_budget(budget["maxBudget"], 0) # budget["minBudget"])
    
    # Get event list
    # event_list = event_list_resale_owned("PublicVH")
    # print(event_list)
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
        media_url = upload_image(image_path)
        print(media_url)

        # Create the event
        ticket_data = [{"name": bought_ticket.name, "price": bought_ticket.price, "media": media_url}]
        data = create_resell_event("PublicVH", event.title, "N/A", "N/A", "N/A","United Kingdom","Fixr", ticket_data=ticket_data)
        print(data)
    
    # Close the driver
    driver.quit()


if __name__ == "__main__":
    main()
