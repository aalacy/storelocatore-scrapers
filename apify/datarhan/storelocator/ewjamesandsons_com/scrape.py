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

    start_url = "https://ewjamesandsons.com/"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="location-data"]')
    for poi_html in all_locations:
        store_url = poi_html.xpath('.//h3[@class="site-loc-name"]/a/@href')[0]
        store_url = urljoin(start_url, store_url)
        location_name = poi_html.xpath('.//h3[@class="site-loc-name"]/a/text()')
        location_name = location_name[-1].strip() if location_name else "<MISSING>"
        street_address = poi_html.xpath('.//div[@class="site-loc-address"]/text()')
        if poi_html.xpath('.//div[@class="site-loc-address2"]/text()'):
            street_address += poi_html.xpath(
                './/div[@class="site-loc-address2"]/text()'
            )
        street_address = " ".join(street_address) if street_address else "<MISSING>"
        raw_data = poi_html.xpath('.//div[@class="site-city-state-zip"]/text()')[0]
        city = raw_data.split(",")[0]
        state = raw_data.split(",")[-1].split()[0]
        zip_code = raw_data.split(",")[-1].split()[-1]
        country_code = "<MISSING>"
        store_number = poi_html.xpath(".//@data-location-id")[0]
        phone = poi_html.xpath('.//div[@class="site-loc-phone"]/text()')
        phone = phone[0].split(":")[-1] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi_html.xpath(".//@data-lat")[0]
        longitude = poi_html.xpath(".//@data-lon")[0]
        hours_of_operation = (
            poi_html.xpath('.//div[@class="site-loc-hours"]/text()')[0]
            .split("Hours:")[-1]
            .strip()
        )

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
