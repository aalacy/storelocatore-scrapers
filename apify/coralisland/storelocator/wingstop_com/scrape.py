import csv
import datetime
import json

from sglogging import sglog

from sgrequests import SgRequests

from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

import usaddress

log = sglog.SgLogSetup().get_logger(logger_name="wingstop_com")

base_url = "https://www.wingstop.com"
page_url = "https://www.wingstop.com/order"


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
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
        # Body
        id_dupes = []
        for row in data:
            if row[8] in id_dupes:
                pass
            else:
                id_dupes.append(row[8])
                writer.writerow(row)


def validate(item):
    if item is None:
        item = ""
    if type(item) == int or type(item) == float:
        item = str(item)
    if type(item) == list:
        item = " ".join(item)
    return item.replace("\u2013", "-").strip()


def get_value(item):
    if item is None:
        item = "<MISSING>"
    item = validate(item)
    if item == "":
        item = "<MISSING>"
    return item


def eliminate_space(items):
    rets = []
    for item in items:
        item = validate(item)
        if item != "":
            rets.append(item)
    return rets


def parse_address(address):
    address = usaddress.parse(address)
    street = ""
    city = ""
    state = ""
    zipcode = ""
    for addr in address:
        if addr[1] == "PlaceName":
            city += addr[0].replace(",", "") + " "
        elif addr[1] == "ZipCode":
            zipcode = addr[0].replace(",", "")
        elif addr[1] == "StateName":
            state = addr[0].replace(",", "") + " "
        else:
            street += addr[0].replace(",", "") + " "
    return {
        "street": get_value(street),
        "city": get_value(city),
        "state": get_value(state),
        "zipcode": get_value(zipcode),
    }


def get_info(store):
    output = []
    latitude = get_value(store["latitude"])
    longitude = get_value(store["longitude"])
    output.append(base_url)  # url
    output.append(page_url)  # page url
    output.append(get_value(store["name"]))  # location name
    output.append(get_value(store["streetaddress"]))  # address
    output.append(get_value(store["city"]))  # city
    output.append(get_value(store["state"]))  # state
    output.append(get_value(store["zip"]))  # zipcode
    output.append(get_value(store["country"]))  # country code
    output.append(get_value(store["id"]))  # store_number
    output.append(get_value(store["telephone"]))  # phone
    output.append("<MISSING>")  # location type
    output.append(latitude)  # latitude
    output.append(longitude)  # longitude
    store_hours = []
    if "calendars" in store and len(store["calendars"]["calendar"]) > 0:
        for hour in store["calendars"]["calendar"][0]["ranges"]:
            start = validate(hour["start"]).split(" ")[-1]
            end = validate(hour["end"]).split(" ")[-1]
            if end == "00:00":
                end = "midnight"
            store_hours.append(validate(hour["weekday"]) + " " + start + "-" + end)
    output.append(get_value(store_hours))  # opening hours
    return output


def fetch_data():

    session = SgRequests()

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    history = []
    data = []

    today = datetime.datetime.utcnow()
    start_datetime = today.strftime("%Y%m%d")
    tomorrow = today + datetime.timedelta(7)
    end_datetime = datetime.datetime.strftime(tomorrow, "%Y%m%d")

    max_distance = 100

    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA], max_search_distance_miles=max_distance
    )

    for lat, lng in search:
        log.info(
            "Searching: %s, %s | Items remaining: %s"
            % (lat, lng, search.items_remaining())
        )

        url = (
            "https://api.wingstop.com/restaurants/near?lat="
            + str(lat)
            + "&long="
            + str(lng)
            + "&radius="
            + str(max_distance)
            + "&limit=100&nomnom=calendars&nomnom_calendars_from="
            + start_datetime
            + "&nomnom_calendars_to="
            + end_datetime
        )
        request = session.get(url, headers=headers)
        if request.status_code != 200:
            session = SgRequests()
            request = session.get(url, headers=headers)

        store_list = json.loads(request.text)["restaurants"]
        for store in store_list:
            if (
                "COMING SOON" in get_value(store["name"]).upper()
                or "closed!" in get_value(store["name"]).lower()
            ):
                continue
            latitude = get_value(store["latitude"])
            longitude = get_value(store["longitude"])
            search.found_location_at(latitude, longitude)

            if get_value(store["id"]) in history:
                continue
            else:
                history.append(get_value(store["id"]))

                output = get_info(store)
                data.append(output)

    # Get GUAM locations
    url = (
        "https://api.wingstop.com/restaurants/near?lat="
        + str(13.4751756)
        + "&long="
        + str(144.7560506)
        + "&radius="
        + str(max_distance)
        + "&limit=100&nomnom=calendars&nomnom_calendars_from="
        + start_datetime
        + "&nomnom_calendars_to="
        + end_datetime
    )
    request = session.get(url, headers=headers)
    if request.status_code != 200:
        session = SgRequests()
        request = session.get(url, headers=headers)

    store_list = json.loads(request.text)["restaurants"]
    for store in store_list:
        if (
            "COMING SOON" in get_value(store["name"]).upper()
            or "closed!" in get_value(store["name"]).lower()
        ):
            continue

        if get_value(store["id"]) in history:
            continue
        else:
            history.append(get_value(store["id"]))

            output = get_info(store)
            data.append(output)

    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
