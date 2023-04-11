from ...primitives.event import Event
from ...primitives.ticket import Ticket as BaseTicket
from ...primitives.ticket import TicketList as BaseTicketList
from ...source.fixr.checkout import Checkout
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Ticket(BaseTicket):
    def __init__(self, driver, name: str, price: float, event: Event, web_element=None):
        super().__init__(driver, name, price, event, web_element)

    def buy(self, amount: int = 1):
        if amount > 10:
            raise ValueError("You can only book 10 tickets at a time")
        ticket_amount_input_box = self.web_element.find_element(By.XPATH, '//input[@type="tel"]')
        ticket_amount_input_box.send_keys(str(amount))

        reserve_button = self.driver.find_element(By.XPATH, '//button[.//span[text()="Reserve"]]')
        reserve_button.click()

        return Checkout(self.driver, self)


class TicketList(BaseTicketList):
    def __init__(self, driver: webdriver, event: Event):
        super().__init__(driver, event)
        self.driver = driver
        self.event = event

        driver.get(event.event_url + "/tickets")

        wait = WebDriverWait(driver, 10)

        # wait for individual tickets to load
        wait.until(EC.presence_of_element_located((By.XPATH, '//div[h3[text()="Individual tickets"]]')))

        ticket_section = driver.find_element(By.XPATH, '//div[h3[text()="Individual tickets"]]')
        tickets = ticket_section.find_elements(By.CSS_SELECTOR, '.hrObei')

        for ticket_element in tickets:
            ticket = ticket_element.text.split("\n")
            ticket_name = ticket[0]
            ticket_price = ticket[1].replace("£", "")

            if ticket_price.lower() == "Free".lower():
                ticket_price = "0"
            t = Ticket(self.driver, ticket_name, float(ticket_price), self.event, ticket_element)
            self.tickets.append(t)
