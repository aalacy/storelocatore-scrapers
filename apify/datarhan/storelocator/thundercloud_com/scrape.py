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
    scraped_items = []

    DOMAIN = "thundercloud.com"
    start_url = "https://thundercloud.com/find-your-location/"

    with SgFirefox() as driver:
        driver.get(start_url)
        dom = etree.HTML(driver.page_source)

    all_locations = dom.xpath('//div[@class="row location-results"]')
    for poi_html in all_locations:
        store_url = "<MISSING>"
        location_name = poi_html.xpath(".//h6/a/text()")
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_address = poi_html.xpath(".//div/small/text()")
        raw_address = [elem.strip() for elem in raw_address if elem.strip()]
        if len(raw_address) == 2:
            raw_address = raw_address[1:]
        store_number = "<MISSING>"
        street_address = location_name
        city = raw_address[0].split(", ")[0]
        state = raw_address[0].split(", ")[-1].split()[0]
        zip_code = raw_address[0].split(", ")[-1].split()[-1]
        country_code = "<MISSING>"
        phone = poi_html.xpath('.//div/strong[contains(text(), ".")]/text()')
        if not phone:
            phone = poi_html.xpath('.//div/strong[contains(text(), "-")]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        temp_closed = poi_html.xpath('.//*[contains(text(), "TEMPORARILY CLOSED")]')
        if temp_closed:
            location_type = "Temp_closed"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hoo = poi_html.xpath('.//p[contains(text(), "Hours:")]/text()')
        hoo_2 = poi_html.xpath(
            './/p[contains(text(), "Hours:")]/following-sibling::p/text()'
        )
        if hoo_2:
            hoo += hoo_2

        hoo = [elem.strip() for elem in hoo if elem.strip()]
        hours_of_operation = (
            " ".join(hoo).replace("Hours:", "").strip() if hoo else "<MISSING>"
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
        check = f"{location_name} {street_address}"
        if check not in scraped_items:
            scraped_items.append(check)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
