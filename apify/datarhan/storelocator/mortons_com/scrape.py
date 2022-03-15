import re
import csv
import json
from lxml import etree
from urllib.parse import urljoin

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
    # Your scraper here
    session = SgRequests()

    items = []

    DOMAIN = "mortons.com"
    start_url = "https://www.mortons.com/locations/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    data = dom.xpath("//script[contains(text(), locations)]/text()")
    all_locations = re.findall("locations: (.+) apiKey:", data[7].replace("\n", ""))[
        0
    ].strip()[:-1]
    all_locations = json.loads(all_locations)

    for poi in all_locations:
        store_url = urljoin(start_url, poi["url"])
        loc_reponse = session.get(store_url)
        loc_dom = etree.HTML(loc_reponse.text)

        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["street"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["city"]
        city = city if city else "<MISSING>"
        state = poi["state"]
        state = state if state else "<MISSING>"
        if len(state) != 2:
            continue
        zip_code = poi["postal_code"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = poi["id"]
        phone = poi["phone_number"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["lat"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["lng"]
        longitude = longitude if longitude else "<MISSING>"
        hoo = loc_dom.xpath('//div[h2[@class="h1"]]/p[2]//text()')
        hoo = [e.strip() for e in hoo if e.strip() and "We " not in e]
        hours_of_operation = (
            " ".join(hoo).split("Parties")[0].split("Inside")[0].strip()
            if hoo
            else "<MISSING>"
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
