import re
import csv
from lxml import etree

from sgselenium.sgselenium import webdriver


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

    start_url = "https://www.lotteplaza.com/locations/"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    with webdriver.Firefox() as driver:
        driver.get(start_url)
        dom = etree.HTML(driver.page_source)

    all_locations = dom.xpath('//a[contains(text(), "View Details")]/@href')
    for store_url in all_locations:
        with webdriver.Firefox() as driver:
            driver.get(store_url)
            loc_dom = etree.HTML(driver.page_source)

        location_name = loc_dom.xpath("//article/div/h1/text()")
        location_name = location_name[0].strip() if location_name else "<MISSING>"
        raw_address = loc_dom.xpath(
            '//h2[contains(text(), "Address")]/following-sibling::p/text()'
        )
        street_address = raw_address[0]
        if street_address.endswith(","):
            street_address = street_address[:-1]
        city = raw_address[1].split(", ")[0]
        city = city if city else "<MISSING>"
        state = raw_address[1].split(", ")[1]
        zip_code = raw_address[1].split(", ")[2]
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = loc_dom.xpath(
            '//h2[contains(text(), "Phone Number")]/following-sibling::p/text()'
        )
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hoo = loc_dom.xpath(
            '//h2[contains(text(), "Hours of Operation")]/following-sibling::p/text()'
        )
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
