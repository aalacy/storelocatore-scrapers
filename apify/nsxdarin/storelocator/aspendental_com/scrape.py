import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("aspendental_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
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


MISSING = "<MISSING>"


def get(data, key):
    return data.get(key, MISSING) or MISSING


def get_phone(data):
    return data.get("mainPhone") or data.get("alternativePhone") or MISSING


def get_hours(data):
    days = [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ]
    hours = data.get("hours")
    if not hours or not len(hours):
        return MISSING

    hours_of_operation = []
    for day in days:
        closed = hours[day].get("isClosed")
        if closed:
            hours_of_operation.append(f"{day}: Closed")
            continue

        openings = hours[day]["openIntervals"]
        day_hours = []
        for interval in openings:
            start = interval["start"]
            end = interval["end"]
            day_hours.append(f"{start}-{end}")

        intervals = ",".join(day_hours)
        hours_of_operation.append(f"{day}: {intervals}")

    return ",".join(hours_of_operation)


def extract(location):
    data = location.get("data")
    locator_domain = "aspendental.com"
    store_number = get(data, "id")
    location_name = get(data, "name")
    location_type = get(data, "type")
    page_url = get(data, "website")

    address = data.get("address")
    street_address = get(address, "line1")
    city = get(address, "city")
    state = get(address, "region")
    postal = get(address, "postalCode")
    country_code = get(address, "countryCode")

    geo = (
        data.get("geocodedCoordinate")
        or data.get("yextDisplayCoordinate")
        or data.get("yextRoutableCoordinate")
        or data.get("cityCoordinate")
    )

    latitude = get(geo, "latitude")
    longitude = get(geo, "longitude")

    phone = get_phone(data)
    hours = get_hours(data)

    poi = {
        "locator_domain": locator_domain,
        "store_number": store_number,
        "location_name": location_name,
        "location_type": location_type,
        "page_url": page_url,
        "street_address": street_address,
        "city": city,
        "state": state,
        "zip": postal,
        "country_code": country_code,
        "latitude": latitude,
        "longitude": longitude,
        "phone": phone,
        "hours_of_operation": hours,
    }

    return [poi[field] for field in FIELDS]


def validate_dup(location, tracker):
    data = location.get("data")
    id = data.get("id")

    return id in tracker, id


def query_locations(page=0, dedup_tracker=[]):
    url = "https://liveapi.yext.com/v2/accounts/me/answers/vertical/query"
    params = {
        "v": "20190101",
        "api_key": "5568aa1809f16997ec2ac0c1ed321f59",
        "sessionTrackingEnabled": True,
        "input": "",
        "experienceKey": "aspen_dental_answers",
        "version": "PRODUCTION",
        "verticalKey": "locations",
        "limit": 50,
        "offset": page * 50,
        "queryId": "878323fa-cfa8-42f2-836f-975b7b1837b9",
        "locale": "en",
    }

    data = session.get(url, params=params, headers=headers).json()
    results = data.get("response").get("results")

    for location in results:
        is_dup, id = validate_dup(location, dedup_tracker)
        if is_dup:
            continue
        dedup_tracker.append(id)

        yield extract(location)

    if len(results):
        yield from query_locations(page + 1, dedup_tracker)


def fetch_data():
    yield from query_locations()


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
