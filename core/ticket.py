from .event import Event
from .checkout import Checkout, FixrCheckout
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Ticket:
    def __init__(self, driver, name: str, price: float, event: Event, web_element=None):
        self.driver = driver
        self.name = name
        self.price = price
        self.web_element = web_element
        self.event = event

    def __repr__(self):
        return f"{self.name} - £{self.price}"


class TicketList:
    def __init__(self, driver, event: Event):
        self.driver = driver
        self.tickets: list[Ticket] = []


class FixrTicket(Ticket):
    def __init__(self, driver, name: str, price: float, event: Event, web_element=None):
        super().__init__(driver, name, price, event, web_element)

    def buy(self, amount: int = 1):
        if amount > 10:
            raise ValueError("You can only book 10 tickets at a time")
        ticket_amount_input_box = self.web_element.find_element(By.XPATH, '//input[@type="tel"]')
        ticket_amount_input_box.send_keys(str(amount))

        reserve_button = self.driver.find_element(By.XPATH, '//button[.//span[text()="Reserve"]]')
        reserve_button.click()

        return FixrCheckout(self.driver, self)


class FixrTicketList(TicketList):
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
            t = FixrTicket(self.driver, ticket_name, float(ticket_price), self.event, ticket_element)
            self.tickets.append(t)

    def filter_by_exclude_keywords(self, keywords: list[str]) -> list[Ticket]:
        """Returns a list of tickets that do not contain any of the keywords"""
        return [t for t in self.tickets if t.name not in keywords]

    def filter_by_budget(self, max_price: float, min_price: float = 0) -> list[Ticket]:
        """Returns a list of tickets that are less than or equal to the max price"""
        return [t for t in self.tickets if t.price <= max_price and t.price >= min_price]
