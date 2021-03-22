import re
import csv
import json
from sgrequests import SgRequests
from sglogging import SgLogSetup
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = SgLogSetup().get_logger("ihop_com")
session = SgRequests()

FIELDS = [
    "locator_domain",
    "page_url",
    "location_name",
    "store_number",
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
    with open("data.csv", "w", newline="") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        writer.writerow(FIELDS)

        for i in data:
            if i:
                writer.writerow(i)


def fetch_locations():
    data = session.get(
        "https://maps.restaurants.ihop.com/api/getAsyncLocations?template=domain&level=domain&lat=35.884558999999996&lng=-78.6117549&radius=10000&limit=10000"
    ).json()

    locations = [parse(marker) for marker in data["markers"]]

    return [location for location in locations]


def parse(marker):
    return json.loads(re.search(r"\{.*\}", marker["info"]).group(0))


def us_ca_pr_only(location):
    return location["country"] in ("US", "CA", "PR")


MISSING = "<MISSING>"


def get(entity, key):
    return entity.get(key, MISSING) or MISSING


def fetch_location(location, session):
    locator_domain = "ihop.com"
    store_number = None

    try:
        store_number = location["fid"]

        page_url = f"https://restaurants.ihop.com/data/{store_number}/"
        (data,) = session.get(page_url).json()

        if not us_ca_pr_only(data):
            return None

        location_name = get(data, "location_name")
        location_type = "Restaurant"

        street_address = get(data, "address_1")
        sub_address = get(data, "address_2")
        if sub_address != MISSING:
            street_address += f", {sub_address}"

        city = get(data, "city")
        state = get(data, "region")
        postal = get(data, "post_code")
        country_code = get(data, "country")

        lat = get(data, "lat")
        lng = get(data, "lng")

        phone = get(data, "local_phone")

        hours = []
        days = data["hours_sets"]["primary"].get("days")

        if days:
            for day in days:
                if isinstance(days[day], list):
                    opening = days[day][0]["open"]
                    close = days[day][0]["close"]
                    hours.append(f"{day}: {opening}-{close}")
                else:
                    hour = days[day]
                    hours.append(f"{day}: {hour}")

            hours_of_operation = ",".join(hours)
        else:
            hours_of_operation = MISSING

        return {
            "locator_domain": locator_domain,
            "store_number": store_number,
            "page_url": page_url,
            "location_name": location_name,
            "location_type": location_type,
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
        logger.error(f"{e} >>> {store_number}")


def fetch_data():
    locations = fetch_locations()

    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(fetch_location, location, session) for location in locations
        ]

        for future in as_completed(futures):
            poi = future.result()
            if poi:
                yield [poi[field] for field in FIELDS]


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
