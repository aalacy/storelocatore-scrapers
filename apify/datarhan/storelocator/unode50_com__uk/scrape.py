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
    # http://en.wikipedia.org/wiki/Extreme_points_of_the_United_Kingdom#Westernmost

    top = 60.850000  # north lat
    left = -8.166667  # west long
    right = 1.766667  # east long
    bottom = 49.85  # south lat

    def uk_borders(latlngs):
        """
        Accepts a list of lat/lng tuples.
        returns the list of tuples that are within the bounding box for the UK.
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
    start_url = "https://www.unode50.com/uk/stores#51.494114,-0.255486"
    response = session.get(start_url)
    dom = etree.HTML(response.text)
    data = dom.xpath('//script[contains(text(), "calendar")]/text()')[0]
    data = json.loads(data)

    for poi in data["*"]["Magento_Ui/js/core/app"]["components"][
        "store-locator-search"
    ]["markers"]:
        latitude = poi["latitude"]
        longitude = poi["longitude"]
        coordinates = [(float(latitude), float(longitude))]
        if not uk_borders(coordinates):
            continue

        store_url = poi["url"]
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

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
        state = addr.state
        state = state if state else "<MISSING>"
        zip_code = addr.postcode
        if not zip_code:
            if len(street_address.split()[-1]) == 3:
                zip_code = " ".join(street_address.split()[-2:])
                street_address = street_address.replace(zip_code, "")
            elif len(street_address.split()[0]) == 3:
                zip_code = " ".join(street_address.split()[:2])
                street_address = street_address.replace(zip_code, "")
        zip_code = zip_code if zip_code else "<MISSING>"
        if len(zip_code.split()[-1]) != 3:
            continue
        country_code = "UK"
        store_number = poi["id"]
        phone = poi["contact_phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        data = loc_dom.xpath(
            '//script[@ type="text/x-magento-init" and contains(text(), "openingHours")]/text()'
        )
        hoo = []
        if data:
            data = json.loads(data[0])
            hours = data["*"]["Magento_Ui/js/core/app"]["components"][
                "smile-storelocator-store"
            ]["schedule"]["openingHours"]
            hours = [e[0] if e else "closed" for e in hours]
            days = [
                "Monday",
                "Tuesday",
                "Wednsday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
            ]
            hoo = list(map(lambda d, h: d + " " + h, days, hours))
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

        check = f"{street_address} {location_name}"
        if check not in scraped_items:
            scraped_items.append(check)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
