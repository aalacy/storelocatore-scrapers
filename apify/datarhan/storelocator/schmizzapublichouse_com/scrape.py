import csv
import demjson
from time import sleep
from lxml import etree

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
    items = []

    DOMAIN = "schmizzapublichouse.com"
    start_url = "https://schmizzapublichouse.com/locations/"

    with SgChrome() as driver:
        driver.get(start_url)
        driver.find_element_by_id("id_location").send_keys("1")
        driver.find_element_by_xpath('//button[@type="submit"]').click()
        sleep(15)
        dom = etree.HTML(driver.page_source)

    all_locations = dom.xpath('//a[contains(text(), "View Location")]/@href')
    for store_url in all_locations:
        with SgChrome() as driver:
            driver.get(store_url)
            loc_dom = etree.HTML(driver.page_source)
        data = loc_dom.xpath(
            '//script[@type="application/ld+json" and contains(text(), "longitude")]/text()'
        )[-1]
        data = demjson.decode(data)

        location_name = data["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = data["address"]["streetAddress"]
        street_address = street_address if street_address else "<MISSING>"
        city = data["address"]["addressLocality"]
        city = city if city else "<MISSING>"
        state = data["address"]["addressRegion"]
        state = state if state else "<MISSING>"
        zip_code = data["address"]["postalCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = data["address"]["addressCountry"]["name"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = "<MISSING>"
        phone = data["telephone"]
        phone = phone if phone else "<MISSING>"
        location_type = data["@type"]
        latitude = data["geo"]["latitude"]
        longitude = data["geo"]["longitude"]
        hours_of_operation = data["openingHours"]
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
