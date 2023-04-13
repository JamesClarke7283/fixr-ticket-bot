from selenium import webdriver
from core.source.fixr.account import Account as FixrAccount
from core.source.fixr.event import Event as FixrEvent
from core.source.fixr.event import EventList as FixrEventList
from core.source.fixr.ticket import TicketList as FixrTicketList
from core.primitives.account import Account
from core.primitives.event import Event, EventList
from core.primitives.ticket import TicketList
import logging
from enum import Enum
from __init__ import LOGLEVEL

logging.basicConfig(level=LOGLEVEL)


class Source(Enum):
    FIXR = "Fixr"


class Broker:
    def __init__(self, driver: webdriver, broker: Source):
        self.driver = driver
        self.broker = broker
        self._account, self._event, self._ticket_list, self._event_list = None, None, None, None

        logging.debug(f"Broker Source chosen:\t'{self.broker.value}'")

        if self.broker == Source.FIXR:
            self._account = FixrAccount
            self._event = FixrEvent
            self._event_list = FixrEventList
            self._ticket_list = FixrTicketList

        logging.debug(f"Broker Account:\t'{self._account}'")
        logging.debug(f"Broker Event:\t'{self._event}'")
        logging.debug(f"Broker TicketList:\t'{self._ticket_list}'")

    @property
    def account(self) -> Account:
        return self._account

    @property
    def event(self) -> Event:
        return self._event

    @property
    def ticket_list(self) -> TicketList:
        return self._ticket_list

    @property
    def event_list(self) -> EventList:
        return self._event_list
