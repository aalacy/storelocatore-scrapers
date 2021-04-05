import re
import csv
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

    start_url = "https://myxperiencefitness.com/"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    with SgFirefox() as driver:
        driver.get(start_url)
        dom = etree.HTML(driver.page_source)

    all_locations = dom.xpath("//h4/a/@href")
    for store_url in all_locations:
        with SgFirefox() as driver:
            driver.get(store_url)
            loc_dom = etree.HTML(driver.page_source)

        location_name = loc_dom.xpath('//h1[@class="entry-title"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_data = loc_dom.xpath('//table[@class="table-location"]//a/text()')
        street_address = raw_data[0].split(",")[0]
        city = " ".join(store_url.split("/")[-2].split("-")[:-2])
        state = store_url.split("/")[-2].split("-")[-2]
        zip_code = store_url.split("/")[-2].split("-")[-1]
        if "blaine-south-mn" in store_url:
            city = "blaine south"
            state = "mn"
            zip_code = "<MISSING>"
        country_code = "US"
        store_number = "<MISSING>"
        phone = raw_data[1]
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hoo = loc_dom.xpath(
            '//th[i[@class="fas fa-clock"]]/following-sibling::td/text()'
        )
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = (
            " ".join(hoo).split("Dec 19 ")[-1].split(" XF")[0] if hoo else "<MISSING>"
        )

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
