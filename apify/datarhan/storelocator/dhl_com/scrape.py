import csv
from sgrequests import SgRequests
from sgzip.static import static_coordinate_list, SearchableCountries
from concurrent.futures import ThreadPoolExecutor, as_completed
from tenacity import retry, stop_after_attempt


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
        for rows in data:
            writer.writerows(rows)


@retry(stop=stop_after_attempt(3))
def fetch_latlng(lat, lng, country, session, tracker):
    url = "https://wsbexpress.dhl.com/ServicePointLocator/restV3/servicepoints"
    params = {
        "servicePointResults": 50,
        "countryCode": country,
        "latitude": lat,
        "longitude": lng,
        "language": "eng",
        "key": "963d867f-48b8-4f36-823d-88f311d9f6ef",
    }
    data = session.get(url, params=params).json()

    if not data.get("servicePoints"):
        return []

    locations = []
    for location in data.get("servicePoints"):
        poi = extract(location)
        store_number = poi[8]
        if store_number not in tracker:
            tracker.append(store_number)
            locations.append(poi)

    return locations


def get_coords(location):
    return [location[11], location[12]]


def extract(poi):
    DOMAIN = "dhl.com"
    store_url = ""
    store_url = store_url if store_url else "<MISSING>"
    location_name = poi["servicePointName"]
    location_name = location_name if location_name else "<MISSING>"
    street_address = poi["address"]["addressLine1"]
    if poi["address"]["addressLine2"]:
        street_address += ", " + poi["address"]["addressLine2"]
    if poi["address"]["addressLine3"]:
        street_address += ", " + poi["address"]["addressLine3"]
    street_address = street_address if street_address else "<MISSING>"
    city = poi["address"]["city"]
    city = city if city else "<MISSING>"
    state = poi["address"]["state"]
    state = state if state else "<MISSING>"
    zip_code = poi["address"]["zipCode"]
    zip_code = zip_code if zip_code else "<MISSING>"
    country_code = poi["address"]["country"]
    country_code = country_code if country_code else "<MISSING>"
    store_number = poi["facilityId"]
    store_number = store_number if store_number else "<MISSING>"
    phone = poi["contactDetails"].get("phoneNumber")
    phone = phone if phone else "<MISSING>"
    location_type = poi["servicePointType"]
    location_type = location_type if location_type else "<MISSING>"
    latitude = poi["geoLocation"]["latitude"]
    longitude = poi["geoLocation"]["longitude"]
    latitude = latitude if latitude else "<MISSING>"
    longitude = longitude if longitude else "<MISSING>"
    hours_of_operation = []
    for elem in poi["openingHours"]["openingHours"]:
        day = elem["dayOfWeek"]
        opens = elem["openingTime"]
        closes = elem["closingTime"]
        hours_of_operation.append("{} {} - {}".format(day, opens, closes))
    hours_of_operation = (
        ", ".join(hours_of_operation).split(", HOLIDAY")[0]
        if hours_of_operation
        else "<MISSING>"
    )

    return [
        DOMAIN,
        store_url,
        location_name,
        street_address,
        city,
        state,
        zip_code,
        country_code,
        store_number,
        phone,
        location_type,
        latitude,
        longitude,
        hours_of_operation,
    ]


def fetch_data():
    tracker = []

    session = SgRequests()
    session.get("https://locator.dhl.com/ServicePointLocator/restV3/appConfig")

    with ThreadPoolExecutor() as executor:
        futures = []
        futures.extend(
            executor.submit(fetch_latlng, lat, lng, "US", session, tracker)
            for lat, lng in static_coordinate_list(5, SearchableCountries.USA)
        )
        futures.extend(
            executor.submit(fetch_latlng, lat, lng, "CA", session, tracker)
            for lat, lng in static_coordinate_list(10, SearchableCountries.CANADA)
        )

        for future in as_completed(futures):
            locations = future.result()
            yield locations


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
