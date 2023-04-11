"""This modules deals with API requests to the VIVUS API"""
import requests
import json


def event_list_resale_owned(lgusername: str, query: str = None):
    """Checks if the ticket has already been purchased"""
    return event_list("resaleOwned", lgusername, query)


def event_list(request_type: str, lgusername: str, query: str = None) -> dict:
    """Gets the event list from the Vivus API"""

    payload = {"type": request_type, "lgusername": lgusername}

    if query is not None:
        payload["query"] = query

    with requests.get("https://api.vivushub.com/eventlist", data=payload) as response:
        if response.status_code == 200:
            print(response.text)
            json_response = response.json()
            return json_response
        else:
            raise Exception(f"Request failed with status code {response.status_code}")


def get_ticket_budget(filter_organiser: str = None, filter_date: str = None) -> dict:
    """Gets the ticket budget from the Vivus API"""
    return get_budget("ticketBudget", filter_organiser, filter_date)


def get_budget(request_type, filterOrganiser=None, filterDate=None):
    payload = {"rType": request_type}

    if filterOrganiser is not None:
        payload["filterOrganiser"] = filterOrganiser

    if filterDate is not None:
        payload["filterDate"] = filterDate

    with requests.post("https://api.vivushub.com/rc/budget", data=payload) as response:
        if response.status_code == 200:
            json_response = response.json()["result"]
            return json_response
        else:
            raise Exception(f"Request failed with status code {response.status_code}")


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


def create_resell_event(lgusername: str, event_name: str, event_start_time: str, event_end_time: str, event_location: str, event_country: str, purchase_source: str, ticket_data: list[dict]) -> str:
    """Creates a resell on the Vivus API"""
    return resell_event(lgusername, event_name, event_start_time, event_end_time, event_location, event_country, purchase_source, "create", ticket_data)


def resell_event(lgusername: str, event_name: str, event_start_time: str, event_end_time: str, event_location: str, event_country: str, purchase_source: str, request_type: str, ticket_data: list[dict]) -> str:
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