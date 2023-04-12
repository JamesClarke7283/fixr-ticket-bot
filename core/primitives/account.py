from selenium import webdriver
import logging
from __init__ import LOGLEVEL

logging.basicConfig(level=LOGLEVEL)


class Account:
    def __init__(self, driver: webdriver, username: str, password: str):
        self.driver = driver
        self.username = username
        self.password = password

    def login():
        raise NotImplementedError
