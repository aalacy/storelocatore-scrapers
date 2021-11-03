import json
import os
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

# The URL being crawled
URL = "https://www.cellularplus.com/locations/"

# The path to this directory
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


# The entry where the store's location data is stored
locations_variable_name = "page.locations = "
# The entry where the user's location data is stored
location_variable_name = "page.location = "


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


def replace_space(name):
    return name.replace(" ", "-").lower()


def time_convert(time):
    hour = time // 100
    minutes = str(time)[-2:]
    if time >= 1200:
        hour -= 12
        meridiem = "PM"
    else:
        meridiem = "AM"
    return str(hour) + ":" + minutes + " " + meridiem


def clean_hours_aux(day):
    store_open = time_convert(day["Open"])
    store_close = time_convert(day["Close"])
    if store_open == store_close:
        return day["DayOfWeek"] + ": Closed"
    return day["DayOfWeek"] + ": " + str(store_open) + " - " + str(store_close)


def clean_hours(hrlst):
    cleaned = [clean_hours_aux(day) for day in hrlst]
    cleaned = ", ".join(cleaned)
    return cleaned


def store_of_json(elt):
    """
    Returns the relevant info for any given CP store
    """
    return SgRecord(
        locator_domain=URL,
        # The page_url is the concatenation of the locator URL, location ID, and name without spaces
        page_url=URL + str(elt["LocationId"]) + "/" + replace_space(elt["Name"]) + "/",
        location_name=elt["Name"],
        street_address=elt["Address"],
        city=elt["City"],
        state=elt["ProvinceAbbrev"],
        zip_postal=elt["PostalCode"],
        country_code=elt["CountryCode"],
        store_number=elt["LocationId"],
        phone=elt["Phone"],
        location_type="<MISSING>",
        latitude=elt["Google_Latitude"],
        longitude=elt["Google_Longitude"],
        hours_of_operation=clean_hours(elt["HoursOfOperation"]),
    )


def csv_of_storelist(storelst):
    """
    Takes a list of python CP stores and writes to [data.csv]
    """
    with SgWriter() as writer:
        for store in storelst:
            writer.write_row(store)


def scrape():
    result = [store_of_json(store) for store in make_request()]
    csv_of_storelist(result)


if __name__ == "__main__":
    scrape()
