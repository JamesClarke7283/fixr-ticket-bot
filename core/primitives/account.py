from selenium import webdriver


class Account:
    def __init__(self, driver: webdriver, username: str, password: str):
        self.driver = driver
        self.username = username
        self.password = password

    def login():
        raise NotImplementedError
