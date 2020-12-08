import re
import csv
import usaddress
from lxml import etree
from collections import OrderedDict

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

    DOMAIN = "landmarkindustries.com"
    start_url = "https://www.landmarkindustries.com/retail.htm"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//td[@width="263"]/p/text()')
    all_locations = " ".join(all_locations).split("\r\n")

    for loc in all_locations:
        loc = loc.replace("\n", "").strip()
        store_url = "<MISSING>"
        location_name = loc.split("/")[0].strip()
        if not location_name:
            continue
        address_raw = loc.split("/")[-1]
        street_address = address_raw.split(",")[0]
        try:
            address_raw = usaddress.tag(address_raw)
            address_raw = OrderedDict(address_raw[0])
            address_raw = dict(address_raw)
        except:
            address_raw = usaddress.parse(address_raw)
            address_raw = OrderedDict(address_raw)
            address_raw = {y: x for x, y in address_raw.items()}
        city = address_raw.get("PlaceName")
        if city:
            street_address = street_address.replace(city, "").strip()
        city = city if city else "<MISSING>"
        state = address_raw.get("StateName")
        state = state if state else "<MISSING>"
        zip_code = address_raw.get("ZipCode")
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = re.findall(r"\d\d\d", location_name)
        store_number = store_number[0] if store_number else "<MISSING>"
        phone = address_raw.get("OccupancyIdentifier")
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
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

        items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
