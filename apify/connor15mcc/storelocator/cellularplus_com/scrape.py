import json
import csv
import os
from typing import NamedTuple
from sgrequests import SgRequests

# The URL being crawled
URL = "https://www.cellularplus.com/locations/"

# The path to this directory
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


# The entry where the store's location data is stored
locations_variable_name = "page.locations = "
# The entry where the user's location data is stored
location_variable_name = "page.location = "


class Store(NamedTuple):
    """
    The class defining objects that represent each store
    """

    locator_domain: str
    page_url: str
    location_name: str
    street_address: str
    city: str
    state: str
    zip: str
    country_code: str
    store_number: str
    phone: str
    location_type: str
    latitude: float
    longitude: float
    hours_of_operations: str


def make_request():
    """
    Returns a JSON object corresponding to Cellular Plus store info
    """
    with SgRequests() as http:
        page = http.get(URL)
        page.raise_for_status()
    entireStr = page.text
    begin = entireStr.find(locations_variable_name)
    end = entireStr.find(location_variable_name, begin + len(locations_variable_name))
    rawLine = entireStr[begin + len(locations_variable_name) : end].strip()
    rawStr = rawLine[:-1]
    return json.loads(rawStr)


def store_of_json(elt):
    """
    Returns the relevant info for any given CP store
    """
    return Store(
        locator_domain="https://www.cellularplus.com/locations/",
        page_url="https://www.cellularplus.com/locations/",
        location_name=elt["Name"],
        street_address=elt["Address"],
        city=elt["City"],
        state=elt["ProvinceAbbrev"],
        zip=elt["PostalCode"],
        country_code=elt["CountryCode"],
        store_number=elt["LocationId"],
        phone=elt["Phone"],
        location_type="<MISSING>",
        latitude=elt["Google_Latitude"],
        longitude=elt["Google_Longitude"],
        hours_of_operations=elt["HoursOfOperation"],
    )


def csv_of_storelist(storelst):
    """
    Takes a list of python CP stores and writes to [data.csv]
    """
    with open((os.path.join(__location__, "data.csv")), "w", encoding="utf8") as file:
        writer = csv.writer(file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(
            [
                "locator_domain",
                "page_url",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
            ]
        )
        for store in storelst:
            writer.writerow(store)


def scrape():
    result = [store_of_json(store) for store in make_request()]
    csv_of_storelist(result)


if __name__ == "__main__":
    scrape()
