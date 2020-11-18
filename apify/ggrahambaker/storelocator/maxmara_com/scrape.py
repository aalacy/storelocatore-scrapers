import csv
from datetime import datetime
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("maxmara_com")


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
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
                "page_url",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


MISSING = "<MISSING>"


def get(location, key):
    return location.get(key, MISSING) or MISSING


def get_state(components):
    state = components[1]
    for d in components[2]:
        if d.isdigit():
            state = MISSING
            break

    return state


def get_country_code(properties):
    country = get(properties, "country")
    if country == "United States":
        return "US"
    if country == "Canada":
        return "CA"

    return country


def get_hours(properties):
    days = properties.get("openingHours")
    if not days:
        return MISSING

    hours = [f"{day}: {val[0]}" for day, val in days.items()]
    return ",".join(hours).strip()


def fetch_data():
    session = SgRequests()
    HEADERS = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }

    countries = ["US", "CA"]
    for country in countries:
        logger.info(f"fetch: {country} locations")
        params = {"listJson": True, "withoutRadius": False, "country": country}

        data = session.get(
            "https://ca.maxmara.com/store-locator",
            params=params,
            headers=HEADERS,
            timeout=1,
        ).json()

        locations = data.get("features")
        logger.info(f"found: {len(locations)} locations")

        for location in locations:

            properties = location.get("properties", {})

            locator_domain = "https://maxmara.com/"
            location_name = get(properties, "displayName")
            store_number = get(properties, "name")

            address = get(properties, "formattedAddress")
            components = address.split(",")

            street_address = components[0]
            city = get(properties, "city")
            state = get_state(components)
            postal = get(properties, "zip")
            country_code = get_country_code(properties)
            lat = get(properties, "lat")
            lng = get(properties, "lng")

            phone_number = get(properties, "phone1")
            hours = get_hours(properties)
            page_url = f"https://world.maxmara.com/store/{get(properties, 'name')}"

            location_type = MISSING

            store_data = [
                locator_domain,
                location_name,
                street_address,
                city,
                state,
                postal,
                country_code,
                store_number,
                phone_number,
                location_type,
                lat,
                lng,
                hours,
                page_url,
            ]

            yield store_data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
