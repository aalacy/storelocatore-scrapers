import csv
import json
from time import sleep
from lxml import etree

from sgselenium.sgselenium import webdriver

profile = webdriver.FirefoxProfile()
profile.set_preference(
    "geo.wifi.uri",
    'data:application/json,{"location": {"lat": 38.912650, "lng":-77.036185}, "accuracy": 20.0}',
)
profile.set_preference("geo.prompt.testing", True)
options = webdriver.FirefoxOptions()
options.headless = True


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

    DOMAIN = "cashwise.com"
    start_url = "https://www.cashwise.com/storelocator"

    driver = webdriver.Firefox(profile, options=options)
    driver.get(start_url)
    sleep(20)
    dom = etree.HTML(driver.page_source)

    all_locations = dom.xpath("//script[@data-yext-id]/text()")
    for poi in all_locations:
        poi = json.loads(poi)
        store_url = poi.get("url")
        store_url = store_url if store_url else "<MISSING>"
        location_name = poi["name"]
        street_address = poi["address"]["streetAddress"]
        city = poi["address"]["addressLocality"]
        state = poi["address"]["addressRegion"]
        zip_code = poi["address"]["postalCode"]
        country_code = "<MISSING>"
        store_number = poi["@id"]
        phone = poi["telephone"]
        location_type = ", ".join(poi["@type"])
        latitude = poi["geo"]["latitude"]
        longitude = poi["geo"]["longitude"]
        hours_of_operation = []
        for elem in poi["openingHoursSpecification"]:
            day = elem["dayOfWeek"]
            hours_of_operation.append(f'{day} {elem["opens"]} - {elem["closes"]}')
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

    driver.close()
    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
