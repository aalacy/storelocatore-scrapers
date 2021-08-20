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

    start_url = "https://www.worldoftile.net/pages/store-locator.html"
    DOMAIN = re.findall("https://www.(.+?)/", start_url)[0]

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//div[@class="locator"]/div[@class="row"]/div[@class="col-md-4"]'
    )[1:]
    for poi_html in all_locations:
        store_url = "https://www.worldoftile.net/pages/store-locator.html"
        location_name = poi_html.xpath(".//h4/text()")
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_address = poi_html.xpath("./p/text()")
        raw_address = [e.strip() for e in raw_address if e.strip()]
        street_address = raw_address[0]
        if street_address.endswith(","):
            street_address = street_address[:-1]
        city = raw_address[1].split(", ")[0]
        state = raw_address[1].split(", ")[-1].split()[0]
        zip_code = raw_address[1].split(", ")[-1].split()[-1]
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = raw_address[-2]
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hoo = poi_html.xpath('.//div[@class="hours"]//text()')[1:]
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

        items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
