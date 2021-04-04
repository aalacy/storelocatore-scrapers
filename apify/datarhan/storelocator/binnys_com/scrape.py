import re
import csv
import demjson
from urllib.parse import urljoin
from w3lib.html import remove_tags

from sgrequests import SgRequests


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
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    session = SgRequests()

    items = []

    DOMAIN = "binnys.com"
    start_url = "https://www.binnys.com/store-locator"

    response = session.post(start_url)
    data = re.findall("serverSideModel =(.+);", response.text)
    data = demjson.decode(data[0])

    for poi in data["storesGroupedByState"][0]:
        store_url = urljoin(start_url, poi["storePageUrl"])
        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["addressLine1"]
        if poi["addressLine2"]:
            street_address += " " + street_address
        city = poi["city"]
        state = poi["state"]
        zip_code = poi["zipCode"]
        country_code = "<MISSING>"
        store_number = poi["id"]
        phone = poi["phoneNumber"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = (
            remove_tags(poi["storeHours"])
            .replace("\n", " ")
            .replace("  ", " ")
            .split("&nbsp;")[0]
            .strip()
        )

        item = [
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

        items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
