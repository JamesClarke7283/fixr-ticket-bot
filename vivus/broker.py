from selenium import webdriver
from core.source.fixr.account import Account as FixrAccount
from core.source.fixr.event import Event as FixrEvent
from core.source.fixr.ticket import TicketList as FixrTicketList
from core.primitives.account import Account
from core.primitives.event import Event
from core.primitives.ticket import TicketList
import logging
from enum import StrEnum
from __init__ import LOGLEVEL

logging.basicConfig(level=LOGLEVEL)


class Source(StrEnum):
    FIXR = "Fixr"


class Broker:
    def __init__(self, driver: webdriver, broker: Source):
        self.driver = driver
        self.broker = broker
        self._account, self._event, self._ticket_list = None, None, None

        logging.debug(f"Broker Source chosen:\t'{self.broker.value}'")

        match self.broker:
            case Source.FIXR:
                self._account = FixrAccount
                self._event = FixrEvent
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
