from sgrequests import SgRequests
from sglogging import SgLogSetup
from datetime import datetime
from datetime import timedelta
import csv

logger = SgLogSetup().get_logger("blazepizza_com")
session = SgRequests()

MISSING = "<MISSING>"
headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
}

FIELDS = [
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


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
        writer.writerow(FIELDS)
        for row in data:
            writer.writerow(row)


def get_hours(location):
    try:
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        calendar = location.get("calendars", {}).get("calendar")
        hours = []
        if calendar and len(calendar) and len(calendar[0].get("ranges", [])):
            weekdays = calendar[0]["ranges"]
            for day in days:
                hour = next(filter(lambda hour: hour["weekday"] == day, weekdays), None)
                if hour:
                    start = hour.get("start").split(" ").pop()
                    end = hour.get("end").split(" ").pop()
                    time_range = f"{start}-{end}"
                else:
                    time_range = "Closed"

                hours.append(f"{day} {time_range}")
        else:
            hours.append("Closed")

        return "; ".join(hours) or MISSING
    except:
        pass


def extract(location, store_number):
    start = (datetime.now() + timedelta(days=-1)).strftime("%Y%m%d")
    end = (datetime.now() + timedelta(days=14)).strftime("%Y%m%d")
    url_hours = "https://nomnom-prod-api.blazepizza.com/restaurants/"
    params = {
        "nomnom": "calendars",
        "nomnom_calendars_from": start,
        "nomnom_calendars_to": end,
    }
    url_hours_store_number = (
        f"https://nomnom-prod-api.blazepizza.com/restaurants/{store_number}"
    )
    hoo_data = session.get(
        url_hours_store_number, headers=headers, params=params
    ).json()
    logger.info(f"[Pulling the data from {url_hours_store_number}]")
    try:
        locator_domain = "blazepizza.com"
        page_url = f"https://nomnom-prod-api.blazepizza.com/restaurants/{store_number}"
        location_name = location.get("name", MISSING)
        location_type = MISSING
        street_address = location.get("streetaddress")
        city = location.get("city")
        state = location.get("state")
        page_url = "https://www.blazepizza.com/locations/" + state + "/" + city
        postal = location.get("zip", MISSING)
        country_code = location.get("country", MISSING)
        lat = location.get("latitude", MISSING)
        lng = location.get("longitude", MISSING)
        phone = location.get("phone", MISSING)
        hours_of_operation = get_hours(hoo_data)
        if ":" not in hours_of_operation:
            hours_of_operation = "<MISSING>"
        return {
            "locator_domain": locator_domain,
            "page_url": page_url,
            "location_name": location_name,
            "location_type": location_type,
            "store_number": store_number,
            "street_address": street_address,
            "city": city,
            "state": state,
            "zip": postal,
            "country_code": country_code,
            "latitude": lat,
            "longitude": lng,
            "phone": phone,
            "hours_of_operation": hours_of_operation,
        }
    except Exception as e:
        logger.error(e)


def get_state_city_based_urls():
    url_containing_state_city_based_data_uri = (
        "https://nomnom-prod-api.blazepizza.com/extras/restaurant/summary/state"
    )
    url_api_base = "https://nomnom-prod-api.blazepizza.com"
    data_uri = session.get(url_containing_state_city_based_data_uri).json()
    url_all_states = []
    for duri in data_uri["data"]:
        uri = duri["cities"][0]["datauri"]
        url_full = f"{url_api_base}{uri}"
        url_all_states.append(url_full)
    return url_all_states


def fetch_data():
    dedup_tracker = []
    list_of_state_urls = get_state_city_based_urls()
    total = 0
    for url in list_of_state_urls:
        logger.info(f"[ Pulling the store URL from {url} ]")
        data = session.get(url, headers=headers).json()
        found = 0
        for location in data["data"][0]["restaurants"]:
            store_number = location.get("id")
            logger.info(f"[ Store Number: {store_number} ]")
            poi = extract(location, store_number)
            yield [poi[field] for field in FIELDS]
            found += 1
        total += found
    logger.info(f"[Scraping Finished] | Total Store Count:{total}]")


def scrape():
    logger.info("Scraping Started...")
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
