import csv
from lxml import etree
from time import sleep

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

    DOMAIN = "chatime.com"
    start_url = "https://chatime.com/locations/?location=7%20Germantown%20Ave,%20Edison,%20NJ%2008817,%20%D0%A1%D0%A8%D0%90&radius=999"

    with SgChrome() as driver:
        driver.get(start_url)
        sleep(15)
        dom = etree.HTML(driver.page_source)

    all_locations = dom.xpath('//div[@class="store_locator_result_list_item"]')
    for poi_html in all_locations:
        store_url = "<MISSING>"
        location_name = poi_html.xpath('.//h3[@class="store_locator_name"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = poi_html.xpath(
            './/span[@class="store_locator_street"]/text()'
        )[0]
        zip_code = poi_html.xpath('.//span[@class="store_locator_zip"]/text()')
        zip_code = zip_code[0] if zip_code else "<MISSING>"
        city = poi_html.xpath('.//span[@class="store_locator_city"]/text()')
        city = city[0].strip() if city else "<MISSING>"
        state = poi_html.xpath('.//span[@class="store_locator_region"]/text()')
        state = state[0] if state else "<MISSING>"
        country_code = "<MISSING>"
        store_number = poi_html.xpath("@id")[0].split("_")[-1]
        phone = poi_html.xpath('.//span[@class="store_locator_tel"]/a/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        geo = (
            poi_html.xpath('.//p[@class="store_locator_actions"]/a/@href')[0]
            .split("=")[-1]
            .split(",")
        )
        latitude = geo[0]
        longitude = geo[1]
        hoo = poi_html.xpath('.//div[@class="store-locator-opening-hours"]//text()')
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

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
