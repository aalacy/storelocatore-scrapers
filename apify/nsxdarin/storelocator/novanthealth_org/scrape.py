import re
import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
}

logger = SgLogSetup().get_logger("novanthealth_org")


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
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
        for row in data:
            writer.writerow(row)


MISSING = "<MISSING>"


def get(entity, key):
    return entity.get(key, MISSING) or MISSING


def fetch_data():
    url = "https://www.novanthealth.org/DesktopModules/NHLocationFinder/API/Location/ByType"
    payload = {
        "LocationGroupId": "1",
        "Latitude": "",
        "Longitude": "",
        "Distance": "5",
        "SubTypes": "",
        "Keyword": "",
        "SortOrder": "",
        "MaxLocations": "2500",
        "MapBounds": "",
    }
    data = session.post(url, headers=headers, data=payload).json()
    locations = data["Locations"]

    for location in locations:
        locator_name = "novanthealth.org"
        page_url = get(location, "WebsiteUrl")
        store_number = get(location, "StoreCode")
        location_name = get(location, "BusinessName")
        location_type = MISSING

        street_name = get(location, "AddressLine")
        city = get(location, "City")
        state = get(location, "State")
        postal = get(location, "PostalCode")
        country_code = "US"

        lat = get(location, "Latitude")
        lng = get(location, "Longitude")

        phone = get(location, "PrimaryPhone")

        hours = []
        for day, hour in location["HoursInfo"]["Display"].items():
            if re.search("open 24 hours", hour, re.IGNORECASE):
                hours.append(hour)
            else:
                hours.append(f"{day}: {hour}")

        hours_of_operation = ",".join(hours) or MISSING

        yield [
            locator_name,
            page_url,
            location_name,
            street_name,
            city,
            state,
            postal,
            country_code,
            store_number,
            phone,
            location_type,
            lat,
            lng,
            hours_of_operation,
        ]


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
