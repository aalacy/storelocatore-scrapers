import re
import json
import csv
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

    DOMAIN = "flyersenergy.com"
    start_url = "https://www.flyersenergy.com/locations/"

    with SgChrome() as driver:
        passed = False
        while not passed:
            driver.get(start_url)
            if driver.page_source == "<html><head></head><body></body></html>":
                passed = False
                continue
            else:
                passed = True

            element = driver.find_element_by_xpath(
                '//button[@class="mgbutton moove-gdpr-infobar-allow-all"]'
            )
            driver.execute_script("arguments[0].click();", element)
            driver.find_element_by_xpath(
                '//button[@class="wpgmza-api-consent"]'
            ).click()
            sleep(60)
            dom = etree.HTML(driver.page_source)
            data = dom.xpath('//script[contains(text(), "marker_data")]/text()')[0]
            data = json.loads(re.findall(r"marker_data = (.+?);", data)[0])

    for poi in data["1"].values():
        store_url = "https://www.flyersenergy.com/locations/"
        location_name = poi["title"]
        street_address = poi["address"].split(", ")[0]
        city = poi["address"].split(", ")[1]
        state = poi["address"].split(", ")[-1].split()[0]
        zip_code = poi["address"].split(", ")[-1].split()[-1]
        latitude = poi["lat"]
        longitude = poi["lng"]
        country_code = "<MISSING>"
        store_number = re.findall(r"(\d+) -", poi["title"])[0]
        phone = "<MISSING>"
        location_type = "<MISSING>"
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
