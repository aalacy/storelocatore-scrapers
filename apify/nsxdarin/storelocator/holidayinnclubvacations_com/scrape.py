import re
import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address, USA_Best_Parser

logger = SgLogSetup().get_logger("holidayinnclubvacations_com")


session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


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


def get(entity, key, default=MISSING):
    return entity.get(key, default) or default


def fetch_data():
    for x in range(1, 4):
        url = f"https://holidayinnclub.com/api/resorts?page={x}"
        data = session.get(url, headers=headers).json()

        for location in data["items"]:
            locator_domain = "holidayinnclubvacations.com"
            location_type = "Hotel"
            hours_of_operation = MISSING

            location_name = get(location, "displayTitle")
            store_number = get(location, "uid")

            slug = get(location, "resortSlugs", None)
            page_url = (
                f"https://holidayinnclub.com/explore-resorts/{slug}"
                if slug
                else MISSING
            )

            contact = location["contactInformation"]
            address = get(contact, "address")
            if not address:
                raise Exception("No address")

            parsed_address = parse_address(
                USA_Best_Parser(), re.sub("\n", ",", address)
            )

            street_address = parsed_address.street_address_1
            city = parsed_address.city
            state = parsed_address.state
            postal = parsed_address.postcode
            country = parsed_address.country

            geolocation = get(location, "coordinates", {})
            lat = get(geolocation, "latitude")
            lng = get(geolocation, "longitude")

            phone = MISSING
            phones = get(contact, "phones")
            if len(phones):
                phone = phones[0]["phoneNumber"]

            yield [
                locator_domain,
                page_url,
                location_name,
                street_address,
                city,
                state,
                postal,
                country,
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
