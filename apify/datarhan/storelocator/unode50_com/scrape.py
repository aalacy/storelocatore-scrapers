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
    # http://en.wikipedia.org/wiki/Extreme_points_of_the_United_States#Westernmost

    top = 49.3457868  # north lat
    left = -124.7844079  # west long
    right = -66.9513812  # east long
    bottom = 24.7433195  # south lat

    def cull(latlngs):
        """Accepts a list of lat/lng tuples.
        returns the list of tuples that are within the bounding box for the US.
        NB. THESE ARE NOT NECESSARILY WITHIN THE US BORDERS!
        """
        inside_box = []
        for (lat, lng) in latlngs:
            if bottom <= lat <= top and left <= lng <= right:
                inside_box.append((lat, lng))
        return inside_box

    # Your scraper here
    session = SgRequests()

    items = []
    scraped_items = []

    DOMAIN = "unode50.com"
    start_url = "https://www.unode50.com/us/stores#34.09510173134606,-118.3993182825743"
    response = session.get(start_url)
    dom = etree.HTML(response.text)
    data = dom.xpath('//script[contains(text(), "calendar")]/text()')[0]
    data = json.loads(data)

    for poi in data["*"]["Magento_Ui/js/core/app"]["components"][
        "store-locator-search"
    ]["markers"]:
        store_url = poi["url"]
        location_name = poi["name"]
        if location_name == "g":
            continue
        if "., .," in poi["address"]:
            continue
        raw_address = poi["address"].replace("\n", ", ").replace("\t", ", ").split(", ")
        raw_address = " ".join([elem.strip() for elem in raw_address if elem.strip()])
        addr = parse_address_intl(raw_address)
        city = addr.city
        city = city if city else "<MISSING>"
        street_address = f"{addr.street_address_1} {addr.street_address_2}".replace(
            "None", ""
        ).strip()
        street_address = street_address if street_address else "<MISSING>"
        state = addr.state
        state = state if state else "<MISSING>"
        zip_code = addr.postcode
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = poi["id"]
        phone = "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["latitude"]
        longitude = poi["longitude"]
        coordinates = [(float(latitude), float(longitude))]
        if not cull(coordinates):
            continue
        hours_of_operation = "<MISSING>"

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

        if store_url not in scraped_items:
            scraped_items.append(store_url)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
