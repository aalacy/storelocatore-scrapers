import re
import csv
import demjson
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
    scraped_items = []

    DOMAIN = "pirtek.co.uk"
    start_url = "https://www.pirtek.co.uk/find-service-centre/"

    response = session.get(start_url)
    all_locations = re.findall(r"addMarker\((.+?)\);", response.text)
    all_locations = [
        e.split(",")[-1].strip()[1:-1] for e in all_locations if "https" in e
    ]
    for store_url in all_locations:
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//h1[@class="post-details--info-title"]/text()')[
            0
        ]
        street_address = loc_dom.xpath('//div[@class="unit-number"]/text()')[0]
        street_address_2 = loc_dom.xpath('//div[@class="street"]/text()')
        if street_address_2:
            street_address += " " + street_address_2[0]
        city = loc_dom.xpath('//div[@class="city"]/text()')[0]
        state = loc_dom.xpath('//div[@class="county"]/text()')
        state = state[0] if state else "<MISSING>"
        zip_code = loc_dom.xpath('//div[@class="postcode"]/text()')
        zip_code = zip_code[0] if zip_code else "<MISSING>"
        phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')
        phone = phone[0] if phone else "<MISSING>"
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        geo = re.findall(r"center: (\{.+?\}),", loc_response.text)[0]
        geo = demjson.decode(geo)
        latitude = geo["lat"]
        longitude = geo["lng"]
        hoo = loc_dom.xpath('//div[@class="open-hours-table"]//text()')
        hoo = [e.strip() for e in hoo if e.strip()]
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
