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

    start_url = "https://www.haleandhearty.com/locations/"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="location-card"]')
    for poi_html in all_locations:
        store_url = start_url
        location_name = poi_html.xpath('.//h3[@class="location-card__name"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = poi_html.xpath(
            './/div[@class="location-card__address"]/p[1]/text()'
        )
        street_address = street_address[0] if street_address else "<MISSING>"
        city = dom.xpath(
            '//div[div[div[h3[contains(text(), "{}")]]]]/h2/text()'.format(
                location_name
            )
        )
        city = "New York"
        state = "<MISSING>"
        zip_code = "<MISSING>"
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = poi_html.xpath('.//p[@class="location-card__phone"]/text()')
        phone = phone[0].split(":")[-1].strip() if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hoo = poi_html.xpath('.//p[@class="location-card__hours-today"]/text()')
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = (
            " ".join(hoo).split("Hours:")[-1].strip() if hoo else "<MISSING>"
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
