import re
import csv
from lxml import etree
from urllib.parse import urljoin

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

    start_url = "https://www.showplaceicon.com/Browsing/Cinemas"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//article[@id="cinema-list"]/div')
    for poi_html in all_locations:
        store_url = poi_html.xpath('.//a[@class="cinema-title"]/@href')[0]
        store_url = urljoin(start_url, store_url)
        location_name = poi_html.xpath('.//a[@class="cinema-title"]/h3/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_address = poi_html.xpath('.//div[@class="contact-address"]/p/text()')
        raw_address = [e.strip() for e in raw_address if e.strip()]
        street_address = raw_address[0]
        if "suit" in raw_address[1].lower():
            street_address += " " + raw_address[1].strip()
        street_address = street_address if street_address else "<MISSING>"
        city = raw_address[-1].split(", ")[0]
        city = city if city else "<MISSING>"
        state = raw_address[-1].split(", ")[-1].split()[0].strip()
        zip_code = raw_address[-1].split(", ")[-1].split()[-1].strip()
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = (
            poi_html.xpath('.//p[@class="contact-phone"]/text()')[0]
            .split(":")[-1]
            .strip()
        )
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = "<MISSING>"

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
