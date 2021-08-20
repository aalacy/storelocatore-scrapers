import re
import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup


logger = SgLogSetup().get_logger("spacenk_com")


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
        for row in data:
            writer.writerow(row)


MISSING = "<MISSING>"


def get(entity, key):
    return entity.get(key, MISSING) or MISSING


def get_url(city, street_address, store_number):
    city_path = re.sub(" ", "-", city).lower()
    street_address_path = re.sub(" ", "-", street_address).lower()
    return f"https://www.spacenk.com/uk/stores.html#!/l/{city_path}/{street_address_path}/{store_number}"


def get_hours(location):
    days = {
        1: "Monday",
        2: "Tuesday",
        3: "Wednesday",
        4: "Thursday",
        5: "Friday",
        6: "Saturday",
        7: "Sunday",
    }
    hours = get(location, "openingHours")

    hours_of_operations = []
    for hour in hours:
        day = days[hour["dayOfWeek"]]
        closed = hour.get("closed", False)

        if closed:
            hours_of_operations.append(f"{day}: Closed")
        else:
            start = hour["from1"]
            end = hour["to1"]
            hours_of_operations.append(f"{day}: {start}-{end}")

    return ", ".join(hours_of_operations)


def fetch_data():
    session = SgRequests()
    url = "https://uberall.com/api/storefinders/bdwTQJoL7hB55B0EimfSmXjiMRV8eg/locations/all"
    params = {"v": "20171219", "language": "en"}

    result = session.get(url, params=params).json()
    locations = result["response"]["locations"]

    for location in locations:
        locator_domain = "spacenk.com"
        store_number = get(location, "id")
        location_name = get(location, "name")
        location_type = MISSING

        street_address = get(location, "streetAndNumber")
        city = get(location, "city")
        state = get(location, "province")
        postal = get(location, "zip")
        country_code = get(location, "country")
        latitude = get(location, "lat")
        longitude = get(location, "lng")

        phone = get(location, "phone")
        page_url = get_url(city, street_address, store_number)
        hours_of_operation = get_hours(location)

        yield [
            locator_domain,
            page_url,
            location_name,
            street_address,
            city,
            state,
            postal,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation,
        ]


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
