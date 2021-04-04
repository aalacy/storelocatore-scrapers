import re
import csv
from lxml import etree

from sgrequests import SgRequests


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

    DOMAIN = "chwinery.com"

    start_url = "https://chwinery.com/locations?near=50210&distance=10000-miles"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//a[contains(text(), "Location Details")]/@href')

    for store_url in all_locations:
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//h1[@class="location-info__heading"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_address = loc_dom.xpath(
            '//div[@class="location-info__details"]/div/p[1]/text()'
        )[:2]
        raw_address = [elem.strip() for elem in raw_address if elem.strip()]
        street_address = "<MISSING>"
        if len(raw_address) == 2:
            street_address = raw_address[0]
        street_address = street_address.strip() if street_address else "<MISSING>"
        city = raw_address[-1].split(", ")[0].strip()
        state = raw_address[-1].split(", ")[-1].split()[0]
        zip_code = raw_address[-1].split(", ")[-1].split()[-1]
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = loc_dom.xpath(
            '//h2[contains(text(),"Contact")]/following-sibling::p/text()'
        )
        phone = phone[-1].split(":")[-1] if phone else "<MISSING>"
        location_type = "<MISSING>"
        is_tc = loc_dom.xpath('//span[contains(@class, "callout-label")]/text()')
        if is_tc:
            if is_tc[0] == "Coming Soon":
                location_type = "Coming Soon"
        geo = re.findall(r"coords\((.+?)\),", loc_response.text)[0].split(",")
        latitude = geo[0]
        latitude = latitude if latitude else "<MISSING>"
        longitude = geo[1]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = loc_dom.xpath('//table[@class="hours-table"]//text()')
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
