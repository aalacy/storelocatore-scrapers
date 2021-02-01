import re
import csv
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
    scraped_items = []

    DOMAIN = "americantiredepot.com"
    start_url = "https://americantiredepot.com/search/store/locations"

    with SgFirefox() as driver:
        driver.get(start_url)
        dom = etree.HTML(driver.page_source)
        all_locations = dom.xpath('//div[@class="stores-list"]')

    for poi_html in all_locations:
        store_url = poi_html.xpath(".//h4/a/@href")[0]
        store_url = urljoin(start_url, store_url)
        location_name = poi_html.xpath(".//h5/text()")
        location_name = location_name[-1].strip() if location_name else "<MISSING>"
        city = poi_html.xpath(".//h4/a/text()")[0]
        if city.split()[-1].isdigit():
            city = city[:-2]
        address_raw = poi_html.xpath('.//p[i[@class="fa fa-map-marker-alt"]]//text()')
        address_raw = [elem.strip() for elem in address_raw if elem.strip()]
        street_address = address_raw[0]
        street_address = " ".join(
            [elem.capitalize() for elem in street_address.split()]
        )
        words = street_address.split()
        street_address = " ".join(sorted(set(words), key=words.index))
        if street_address.endswith(city):
            street_address = street_address.replace(city, "")
        state = address_raw[-1].split()[0]
        zip_code = address_raw[-1].split()[-1]
        country_code = "<MISSING>"
        store_number = re.findall(r"storeid=(\d+)&", store_url)
        store_number = store_number[0] if store_number else "<MISSING>"
        phone = poi_html.xpath('.//p[i[@class="fa fa-phone-alt"]]/text()')
        phone = phone[0].strip() if phone else "<MISSING>"
        location_type = "<MISSING>"
        if "Coming Soon" in city:
            city = city.split("-")[0].strip()
            location_type = "Coming Soon"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = poi_html.xpath(
            './/table[@class="tbl-store-hours mt-2"]//text()'
        )
        hours_of_operation = [
            elem.strip() for elem in hours_of_operation if elem.strip()
        ]
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
        check = "{} {}".format(location_name, street_address)
        if check not in scraped_items:
            scraped_items.append(check)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
