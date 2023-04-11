from selenium import webdriver


class Event:
    def __init__(self, driver: webdriver, event_url: str):
        self.driver = driver
        self.event_url = event_url

        # Get Event Page
        driver.get(event_url)

    @property
    def title(self) -> str:
        """The name of the event"""
        raise NotImplementedError

    @property
    def organizer(self) -> str:
        """The name of the organizer of the event"""
        raise NotImplementedError

    @property
    def poster_url(self) -> str:
        """The media URL of the poster for the event"""
        raise NotImplementedError

    @property
    def price_from_raw(self) -> str:
        """The raw price from string, contains the Tickets from and the £ symbol with the price"""
        raise NotImplementedError

    @property
    def price_from(self) -> float:
        """The price from as a float, without the Tickets from and the £ symbol"""
        raise NotImplementedError

    @property
    def description(self) -> str:
        """Information about the event"""
        raise NotImplementedError

    @property
    def all_properties(self):
        """Returns a dictionary of all the properties"""
        raise NotImplementedError


class EventList:
    def __init__(self, driver: webdriver, event_list_url: str):
        self.driver = driver
        self.event_list_url = event_list_url

        # Get Event List Page
        driver.get(event_list_url)

    @property
    def events(self) -> list[Event]:
        """A list of all events on the page"""
        raise NotImplementedError