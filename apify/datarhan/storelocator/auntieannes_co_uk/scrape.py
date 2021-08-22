import re
import csv
import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl


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

    DOMAIN = "auntieannes.co.uk"
    start_url = "https://www.auntieannes.co.uk/locations/"

    response = session.get(start_url)
    data = re.findall('data_db":(.+)};jQuery', response.text)[0]
    data = json.loads(data)

    for poi in data["objects"]:
        store_url = start_url
        location_name = poi["store_name"]
        addr = parse_address_intl(poi["location"]["address"]["formatted"])
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        city = poi["location"]["address"].get("postal_town")
        if not city:
            city = poi["location"]["address"]["locality"]
        state = poi["location"]["address"].get("administrative_area_level_2")
        if not state:
            state = poi["location"]["address"]["administrative_area_level_1"]
        state = state if state else "<MISSING>"
        zip_code = poi["location"]["address"].get("postal_code")
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["location"]["address"]["country_short"]
        store_number = poi["id"]
        phone = "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["location"]["lat"]
        longitude = poi["location"]["lng"]
        hoo = []
        if poi["opening_hours"]:
            hoo = etree.HTML(poi["opening_hours"]).xpath("//text()")
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

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
