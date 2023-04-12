from os import environ as os_environ
import logging


LOGLEVEL = os_environ.get('LOGLEVEL', 'INFO').upper()
logging.basicConfig(level=LOGLEVEL)