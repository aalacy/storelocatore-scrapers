import csv
from sglogging import SgLogSetup
from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

logger = SgLogSetup().get_logger("gmc_com")
session = SgRequests()

request_count = 0
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


def get_session(reset=False):
    global session
    global request_count

    if request_count >= 10 or reset:
        request_count = 0
        session = SgRequests()

    return session


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
        writer.writerow(FIELDS)
        for row in data:
            writer.writerow(row)


def get_hours(location):
    hours = []
    days = [None, "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

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
            hours.append(f"{days[day]}: {open_from}-{open_to} ")

    return ",".join(hours)


def fetch_locations(coord, tracker, retry_count=0):
    global request_count
    lat, lng = coord

    url = f"https://www.gmc.com/OCRestServices/dealer/latlong/v1/GMC//{lat}/{lng}"
    params = {"distance": 500, "filterByType": "services", "maxResults": 50}

    try:
        result = (
            get_session(retry_count > 0)
            .get(url, params=params, headers=headers, timeout=1)
            .json()
        )
        request_count += 1
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
        logger.error(e)
        return []


def fetch_data():
    dedup_tracker = []
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA, SearchableCountries.CANADA],
        max_search_results=50,
        max_radius_miles=100,
    )

    for coord in search:
        coords = []
        locations = fetch_locations(coord, dedup_tracker)

        if not len(locations):
            continue

        for location in locations:
            coords.append((location.get("latitude"), location.get("longitude")))
            yield [location[field] for field in FIELDS]

        search.mark_found(coords)
        logger.info(
            f"locations found {len(dedup_tracker)} | items remaining: {search.items_remaining()}"
        )


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == '__main__':
    scrape()
