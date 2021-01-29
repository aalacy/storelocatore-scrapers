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

    DOMAIN = "hibdontire.com"
    start_url = "https://local.hibdontire.com/"

    driver = webdriver.Firefox()
    driver.get(start_url)
    dom = etree.HTML(driver.page_source)
    driver.close()
    all_locations = dom.xpath('//li[@itemtype="http://schema.org/LocalBusiness"]')

    for poi_html in all_locations:
        store_url = poi_html.xpath(".//h3/a/@href")[0]
        location_name = poi_html.xpath(".//h3/a/text()")
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = poi_html.xpath('.//div[@itemprop="streetAddress"]/text()')
        street_address = street_address[0] if street_address else "<MISSING>"
        city = poi_html.xpath('.//span[@itemprop="addressLocality"]/text()')
        city = city[0][:-1] if city else "<MISSING>"
        state = poi_html.xpath('.//span[@itemprop="addressRegion"]/text()')
        state = state[0] if state else "<MISSING>"
        zip_code = poi_html.xpath('.//span[@itemprop="postalCode"]/text()')
        zip_code = zip_code[0] if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = poi_html.xpath('.//a[@itemprop="telephone"]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hoo = poi_html.xpath('.//dl[@class="list-hours"]//text()')
        hoo = [elem.strip() for elem in hoo if elem.strip()]
        hours_of_operation = ", ".join(hoo) if hoo else "<MISSING>"

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
