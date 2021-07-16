import re
import csv
import json
from lxml import etree

from sgselenium import SgFirefox


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
    items = []

    start_url = "https://www.theunionkitchen.com/locations"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")

    with SgFirefox() as driver:
        driver.get(start_url)
        dom = etree.HTML(driver.page_source)

    data = dom.xpath('//script[@class="js-react-on-rails-component"]/text()')[0]
    data = json.loads(data)
    all_locations = data["preloadQueries"][4]["data"]["restaurant"]["pageContent"][
        "sections"
    ][0]["locations"]
    for poi in all_locations:
        store_url = start_url
        street_address = poi["streetAddress"].replace("\n", "")
        if street_address.endswith(","):
            street_address = street_address[:-1]
        location_name = poi["name"]
        city = poi["city"]
        state = poi["state"]
        zip_code = poi["postalCode"]
        country_code = poi["country"]
        store_number = poi["id"]
        phone = poi["phone"]
        location_type = "<MISSING>"
        latitude = poi["lat"]
        longitude = poi["lng"]
        hoo = poi["schemaHours"]
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

        item = [
            domain,
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
