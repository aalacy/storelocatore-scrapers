import re
import csv
import json
from lxml import etree
from urllib.parse import urljoin

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

    start_url = "https://www.netcostmarket.com/locations/"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")

    with SgFirefox() as driver:
        driver.get(start_url)
        dom = etree.HTML(driver.page_source)

    all_locations = dom.xpath('//a[@class="stores_location-el-address"]/@href')
    for url in all_locations:
        store_url = urljoin(start_url, url)
        with SgFirefox() as driver:
            driver.get(store_url)
            loc_dom = etree.HTML(driver.page_source)
        poi = loc_dom.xpath('//script[@type="application/ld+json"]/text()')[0]
        poi = json.loads(poi)
        all_poi = poi["address"]

        location_name = loc_dom.xpath("//h1/text()")
        location_name = "".join(location_name) if location_name else "<MISSING>"
        raw_address = loc_dom.xpath(
            '//div[@data-widget_type="text-editor.default"]/div/div/p/text()'
        )[:2]
        street_address = raw_address[0]
        city = raw_address[1].split(", ")[0].split("NY")[0].strip()
        state = store_url.split("/")[4].upper()
        zip_code = raw_address[1].split(", ")[-1].split()[-1]
        country_code = "US"
        store_number = "<MISSING>"
        phone = [
            e["telephone"] for e in all_poi if street_address[:-1] in e["streetAddress"]
        ]
        if not phone:
            phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        geo = (
            loc_dom.xpath("//iframe/@data-src")[0]
            .split("!2d")[-1]
            .split("!2m")[0]
            .split("!3d")
        )
        latitude = geo[-1].split("!")[0]
        longitude = geo[0]
        hoo = loc_dom.xpath('//div[p[contains(text(), "Monday – Sunday")]]/p//text()')[
            :2
        ]
        if not hoo:
            hoo = loc_dom.xpath(
                '//div[p[contains(text(), "Monday – Saturday")]]/p/text()'
            )[:4]
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
