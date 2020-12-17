import csv
from lxml import etree
from sgrequests import SgRequests
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
    session = SgRequests()

    items = []

    DOMAIN = "specsonline.com"
    start_url = "https://specsonline.com/curbside/"
    with SgChrome() as driver:
        driver.get(start_url)
        dom = etree.HTML(driver.page_source)

    all_locations = dom.xpath('//div[@class="instore-store "]')
    all_locations += dom.xpath('//div[@class="instore-store hidden-stores"]')

    for poi_html in all_locations:
        store_url = "<MISSING>"
        location_name = poi_html.xpath('.//h3[@class="store-title"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        if poi_html.xpath('.//div[@class="store-address"]//text()'):
            address_raw = poi_html.xpath('.//div[@class="store-address"]//text()')
            street_address = " ".join(address_raw[0].split()[1:])
            city = address_raw[1].split(",")[0]
            state = address_raw[1].split(",")[-1]
            zip_code = address_raw[0].split()[0]
        else:
            street_address = "<MISSING>"
            city = "<MISSING>"
            state = "<MISSING>"
            zip_code = "<MISSING>"
        country_code = "<MISSING>"
        store_number = poi_html.xpath('.//input[@name="store-number"]/@value')[0]
        phone = poi_html.xpath('.//div[@class="store-phone"]/a/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
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
