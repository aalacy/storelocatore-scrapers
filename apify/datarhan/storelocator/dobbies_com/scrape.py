import csv
import json
from lxml import etree
from time import sleep

from sgrequests import SgRequests
from sgselenium import SgChrome


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

    DOMAIN = "dobbies.com"
    start_url = "https://www.dobbies.com/api/storedetails?_csrf=0eff4afa-6471-435a-9b42-06d54e2a2d90"

    response = session.get(start_url)
    data = json.loads(response.text)

    for poi in data:
        store_url = "https://www.dobbies.com/content/extended/find-a-garden-centre/{}.html".format(
            poi["name"].lower().replace(" ", "-")
        )
        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["storeAddress"]["street"]
        if poi["storeAddress"]["houseNumber"]:
            street_address += ", " + poi["storeAddress"]["houseNumber"]
        city = poi["storeAddress"]["city"]
        city = city if city else "<MISSING>"
        state = "<MISSING>"
        zip_code = poi["storeAddress"]["postcode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["storeAddress"]["countryCode"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = "<MISSING>"
        phone = "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["position"]["lat"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["position"]["lng"]
        longitude = longitude if longitude else "<MISSING>"

        with SgChrome() as driver:
            driver.get(store_url)
            sleep(2)
            loc_dom = etree.HTML(driver.page_source)
        hours_of_operation = loc_dom.xpath('//div[@class="x-storeHours"]/p/text()')
        hours_of_operation = (
            " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
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
