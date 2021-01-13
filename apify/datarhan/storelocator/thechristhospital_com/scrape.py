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

    DOMAIN = "thechristhospital.com"
    start_url = "https://www.thechristhospital.com/locations"
    all_locations = []
    with SgChrome() as driver:
        driver.get(start_url)
        sleep(3)
        driver.find_element_by_id("btnSearchAdvanced").click()
        sleep(5)
        dom = etree.HTML(driver.page_source)
        all_locations += dom.xpath('//div[@class="location"]')
        next_page = driver.find_element_by_xpath('//a[contains(@id, "PageFwd")]')
        while next_page:
            next_page.click()
            sleep(8)
            dom = etree.HTML(driver.page_source)
            all_locations += dom.xpath('//div[@class="location"]')
            try:
                next_page = driver.find_element_by_xpath(
                    '//a[contains(@id, "PageFwd")]'
                )
            except:
                next_page = ""

    for poi_html in all_locations:
        store_url = "<MISSING>"
        location_name = poi_html.xpath(
            './/span[@class="location-header no-details-link"]/text()'
        )
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = poi_html.xpath('.//span[@class="addressline"]/text()')[
            0
        ].strip()
        address_2 = poi_html.xpath('.//span[@class="addressline addressline2"]/text()')
        if address_2:
            street_address += ", " + address_2[0].strip()
        address_raw = poi_html.xpath('.//span[@class="addressline"]/text()')
        address_raw = [elem.strip() for elem in address_raw if elem.strip()]
        city = address_raw
        city = city[-1].strip().split(",")[0] if city else "<MISSING>"
        state = address_raw
        state = state[-1].strip().split(",")[-1].split()[0] if state else "<MISSING>"
        zip_code = address_raw
        zip_code = (
            zip_code[-1].strip().split(",")[-1].split()[-1] if zip_code else "<MISSING>"
        )
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = poi_html.xpath('.//span[@class="phonenumber"]//a/text()')
        phone = phone[0].strip() if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = poi_html.xpath('.//div[@class="hours"]//text()')
        hours_of_operation = [
            elem.strip() for elem in hours_of_operation if elem.strip()
        ]
        if hours_of_operation == ["Hours"]:
            hours_of_operation = ""
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
