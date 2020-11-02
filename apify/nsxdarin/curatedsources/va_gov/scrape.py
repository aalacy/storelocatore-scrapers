import csv
from sgrequests import SgRequests

MISSING = "<MISSING>"
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

fields = [
    "locator_domain",
    "page_url",
    "store_number",
    "location_name",
    "location_type",
    "street_address",
    "city",
    "state",
    "zip",
    "country_code",
    "latitude",
    "longitude",
    "phone",
    "hours_of_operation",
]


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
        writer.writerow(fields)
        for row in data:
            writer.writerow(row)


def get_hours(hours):
    if not hours:
        return MISSING

    days = [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ]

    return ",".join(f"{day} {hours[day]}" for day in days)


def extract(data):
    locator_domain = "va.gov"
    country_code = "US"

    page_url = data.get("website", MISSING) or MISSING
    store_number = data.get("id", MISSING)
    location_name = data.get("name", MISSING)
    location_type = data.get("facility_type", MISSING)

    address = data.get("address", {}).get("physical", {})
    street_address = address.get("address_1", MISSING)
    city = address.get("city", MISSING)
    state = address.get("state", MISSING)
    postal = address.get("zip", MISSING)
    latitude = data.get("lat", MISSING)
    longitude = data.get("long", MISSING)

    phone = data.get("phone").get("main", MISSING)
    hours_of_operation = get_hours(data.get("hours"))

    return {
        "locator_domain": locator_domain,
        "page_url": page_url,
        "store_number": store_number,
        "location_name": location_name,
        "location_type": location_type,
        "street_address": street_address,
        "city": city,
        "state": state,
        "zip": postal,
        "country_code": country_code,
        "latitude": latitude,
        "longitude": longitude,
        "hours_of_operation": hours_of_operation,
        "phone": phone,
    }


def fetch_data():
    url = "https://api.va.gov/v1/facilities/va?bbox[]=-179&bbox[]=10&bbox[]=-60&bbox[]=70&page=1&per_page=10000"
    query = session.get(url, headers=headers).json()
    locations = query.get("data")

    for location in locations:
        data = location.get("attributes")
        poi = extract(data)
        yield [poi[field] for field in fields]


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
