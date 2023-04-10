"""This modules deals with API requests to the VIVUS API"""
import requests
import json


def get_excluded_keywords(organizer: str = None) -> list[str]:
    """Gets the forbidden keywords from the Vivus API"""
    excluded_keywords = []
    if organizer is None:
        data = {"filterType": "filterTicketKeyword"}
    else:
        data = {"filterType": "filterTicketKeyword", "filterOrganizer": organizer}
    with requests.post("https://api.vivushub.com/rc/filter", data=data) as r:
        excluded_keywords = r.json()["result"]
    return excluded_keywords


def create_resell_event(lgusername: str, event_name: str, event_start_time: str, event_end_time: str, event_location: str, event_country: str, purchase_source: str, request_type: str, ticket_data: list[dict]) -> str:
    """Creates a resell on the Vivus API"""
    request_data = {"lgusername": lgusername,
    "data":{
        "eventname": event_name,
        "eventstime": event_start_time,
        "eventetime": event_end_time,
        "eventlocation": event_location,
        "eventcountry": event_country,
        "purchaseSource": purchase_source,
        "rType": request_type
    },
    "tickData": ticket_data,
    }
    print(json.dumps(request_data, indent=4))

    with requests.post("https://api.vivushub.com/createResell", json=request_data) as r:
        print(r.text)
        return r.text