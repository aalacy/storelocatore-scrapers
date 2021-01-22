import csv
import threading
from sgrequests import SgRequests
from sgzip.static import static_coordinate_list, SearchableCountries
from sglogging import SgLogSetup
from datetime import datetime
from datetime import timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

local = threading.local()
logger = SgLogSetup().get_logger("blazepizza_com")

MISSING = "<MISSING>"
headers = {
    "user-agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0",
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


def get_session():
    if not hasattr(local, "session"):
        local.request_count = 0
        local.session = SgRequests()

    if local.request_count >= 10:
        local.request_count = 0
        local.session = SgRequests()

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

        return ",".join(hours) or MISSING
    except:
        pass


def extract(location, store_number):
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
        hours_of_operation = get_hours(location)
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


def log_status_every_n_coords(n, locations, completed, total):
    if completed % n == 0:
        logger.info(
            f"locations found {locations} | remaining coords: {completed}/{total}"
        )


def fetch_locations(coord, dedup_tracker):
    lat = coord[0]
    lng = coord[1]
    start = (datetime.now() + timedelta(days=-1)).strftime("%Y%m%d")
    end = (datetime.now() + timedelta(days=14)).strftime("%Y%m%d")

    url = "https://nomnom-prod-api.blazepizza.com/restaurants/near"
    params = {
        "lat": lat,
        "long": lng,
        "radius": 500,
        "limit": 20,
        "nomnom": "calendars",
        "nomnom_calendars_from": start,
        "nomnom_calendars_to": end,
        "nomnom_exclude_extref": 999,
    }

    data = get_session().get(url, headers=headers, params=params, timeout=0.5).json()
    local.request_count += 1

    for location in data.get("restaurants", []):
        store_number = location.get("id")
        if store_number in dedup_tracker:
            continue

        dedup_tracker.append(store_number)
        poi = extract(location, store_number)
        yield [poi[field] for field in FIELDS]


def fetch_data():
    dedup_tracker = []
    completed = 0
    coords = static_coordinate_list(40, SearchableCountries.USA)
    coords.extend(static_coordinate_list(25, SearchableCountries.CANADA))

    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(fetch_locations, coord, dedup_tracker) for coord in coords
        ]
        for future in as_completed(futures):
            completed += 1
            log_status_every_n_coords(50, len(dedup_tracker), completed, len(coords))
            yield from future.result()


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
