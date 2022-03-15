import csv
from lxml import etree
from time import sleep

from sgselenium import SgFirefox
from sgscrape.sgpostal import parse_address_intl


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

    DOMAIN = "clothesmentor.com"
    start_url = "https://shop-clothes-mentor.myshopify.com/pages/store-locator-1"
    with SgFirefox(is_headless=False) as driver:
        driver.get(start_url)
        sleep(30)
        driver.save_screenshot("clothes.png")
        dom = etree.HTML(driver.page_source)

    all_locations = dom.xpath('//li[contains(@id, "storemapper-listing")]')
    for poi_html in all_locations:
        store_url = poi_html.xpath('.//p[@class="storemapper-url"]/a/@href')[0]
        location_name = poi_html.xpath('.//h4[@class="storemapper-title"]/text()')[0]
        street_address = poi_html.xpath('.//p[@class="storemapper-address"]/text()')[0]
        addr = parse_address_intl(
            location_name.split("#")[0].replace("Store", "").strip()
        )
        if "," in location_name:
            city = location_name.split(", ")[0]
            state = location_name.split(", ")[-1].split()[0]
        else:
            city = addr.city
            state = addr.state
        zip_code = "<MISSING>"
        country_code = "<MISSING>"
        store_number = location_name.split("#")[-1]
        phone = poi_html.xpath('.//p[@class="storemapper-phone"]/a/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi_html.xpath(".//a/@data-lat")[0]
        longitude = poi_html.xpath(".//a/@data-lng")[0]
        hoo = poi_html.xpath('.//p[@class="storemapper-custom-1"]/text()')
        hoo = [elem.strip() for elem in hoo if elem.strip()]
        hours_of_operation = (
            " ".join(hoo).split("Store Hours: ")[-1] if hoo else "<MISSING>"
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
