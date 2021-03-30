import csv
import time
import random
import threading
from sglogging import SgLogSetup
from sgrequests import SgRequests
from sgzip.static import static_coordinate_list, SearchableCountries
from concurrent.futures import ThreadPoolExecutor, as_completed

local = threading.local()
logger = SgLogSetup().get_logger("gmc_com")

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "locale": "en_US",
}

MISSING = "<MISSING>"
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


def sleep():
    duration = random.randint(2, 5)
    time.sleep(duration)


def get_session(reset=False):
    global local
    if not hasattr(local, "session") or reset:
        local.request_count = 0
        local.session = SgRequests().requests_retry_session(retries=0)

    return local.session


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
        writer.writerow(FIELDS)
        for row in data:
            writer.writerow(row)


def get_hours(location):
    hours = {}
    days = [None, "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    week_days = days[1:]

    opening_hours = (
        location.get("generalOpeningHour")
        or location.get("serviceOpeningHour")
        or location.get("partsOpeningHour")
    )

    if not opening_hours or not len(opening_hours):
        return MISSING

    for timeframe in opening_hours:
        open_from = timeframe["openFrom"]
        open_to = timeframe["openTo"]
        for day in timeframe["dayOfWeek"]:
            day_name = days[day]
            hours[day_name] = f"{open_from}-{open_to}"

    for day in week_days:
        if day not in hours:
            hours[day] = "Closed"

    return ",".join(f"{day}: {hours[day]}" for day in week_days)


def fetch_locations(coord, tracker, retry_count=0):
    global local
    lat, lng = coord

    url = f"https://www.gmc.com/OCRestServices/dealer/latlong/v1/GMC/{lat}/{lng}"
    params = {"distance": 500, "maxResults": 50}

    try:
        sleep()
        result = (
            get_session(retry_count > 0).get(url, params=params, headers=headers).json()
        )
        local.request_count += 1
        if not result["payload"] or not result["payload"]["dealers"]:
            return []

        locations = result["payload"]["dealers"]
        data = []
        for location in locations:
            store_number = location["id"]
            if store_number in tracker:
                continue

            tracker.append(store_number)
            locator_domain = "gmc.com"
            location_type = "Dealer"
            location_name = location.get("dealerName", MISSING)
            page_url = location.get("dealerUrl", MISSING)

            address = location["address"]
            street_address = address.get("addressLine1", MISSING)
            city = address.get("cityName", MISSING)
            state = address.get("countrySubdivisionCode", MISSING)
            postal = address.get("postalCode", MISSING)
            country_code = address.get("countryIso", MISSING)

            geolocation = location["geolocation"]
            latitude = geolocation.get("latitude", MISSING)
            longitude = geolocation.get("longitude", MISSING)

            contact = location["generalContact"]
            phone = contact.get("phone1") or contact.get("phone2") or MISSING

            hours_of_operation = get_hours(location)

            data.append(
                {
                    "store_number": store_number,
                    "locator_domain": locator_domain,
                    "location_type": location_type,
                    "location_name": location_name,
                    "page_url": page_url,
                    "street_address": street_address,
                    "city": city,
                    "state": state,
                    "zip": postal,
                    "country_code": country_code,
                    "latitude": latitude,
                    "longitude": longitude,
                    "phone": phone,
                    "hours_of_operation": hours_of_operation,
                }
            )
        return data

    except Exception as e:
        if retry_count < 3:
            return fetch_locations(coord, tracker, retry_count + 1)
        logger.error(f"unable to fetch locations for {lat}, {lng} >>>> {e}")
        return []


def log(locations, completed, total):
    if completed % 25 == 0 or completed == total:
        logger.info(
            f"locations found {locations} | items remaining: {completed}/{total}"
        )


def fetch_data():
    completed = 0
    dedup_tracker = []
    search = static_coordinate_list(radius=50, country_code=SearchableCountries.USA)
    search.extend(
        static_coordinate_list(radius=50, country_code=SearchableCountries.CANADA)
    )

    with ThreadPoolExecutor() as executor:
        logger.info(f"starting {executor._max_workers} workers")
        futures = [
            executor.submit(fetch_locations, coord, dedup_tracker) for coord in search
        ]

        for future in as_completed(futures):
            completed += 1

            for location in future.result():
                yield [location[field] for field in FIELDS]

            log(len(dedup_tracker), completed, len(search))


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
