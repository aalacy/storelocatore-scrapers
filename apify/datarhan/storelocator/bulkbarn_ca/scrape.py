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
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []

    start_url = "https://www.bulkbarn.ca/store_selector/en/"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath("//div[@data-jplist-item]")
    for poi_html in all_locations:
        store_url = start_url
        location_name = poi_html.xpath('.//td[@class="sLeft"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_data = poi_html.xpath('.//td[div[@style="display:none;"]]/text()')
        raw_data = [e.strip() for e in raw_data if e.strip()]
        street_address = raw_data[0]
        if street_address.endswith(","):
            street_address = street_address[:-1]
        city = raw_data[1].split(",")[0]
        state = raw_data[1].split(",")[-1].strip()
        zip_code = "<MISSING>"
        country_code = "<MISSING>"
        store_number = location_name.replace("#", "")
        phone = raw_data[-1]
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hoo = poi_html.xpath('.//table[@class="table-borderless"]//text()')
        hoo = [e.strip() for e in hoo if e.strip() and e != "&nbsp"]
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

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
