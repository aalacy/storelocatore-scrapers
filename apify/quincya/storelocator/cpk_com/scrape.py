import csv
import re

from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w") as output_file:
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
        for row in data:
            writer.writerow(row)


def fetch_data():

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    base_link = "https://api.cpk.com/api/v1.0/restaurants/cpk-stores"

    session = SgRequests()
    stores = session.get(base_link, headers=headers).json()["data"]["restaurants"]

    data = []
    locator_domain = "cpk.com"

    for store in stores:
        location_name = store["name"]
        street_address = store["address"].strip()

        digit = re.search(r"\d", street_address).start(0)
        if digit != 0:
            street_address = street_address[digit:]

        city = store["city"]
        state = store["state"]
        zip_code = store["zip"]
        country_code = "US"
        store_number = store["id"]
        location_type = "<MISSING>"
        phone = store["telephone"]
        hours_of_operation = "<INACCESSIBLE>"
        latitude = store["latitude"]
        longitude = store["longitude"]
        link = "<MISSING>"
        # Store data
        data.append(
            [
                locator_domain,
                link,
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
        )
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
