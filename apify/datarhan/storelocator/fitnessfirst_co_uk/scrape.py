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
    session = SgRequests().requests_retry_session(retries=0, backoff_factor=0.3)

    items = []

    DOMAIN = "fitnessfirst.co.uk"
    start_url = "https://www.fitnessfirst.co.uk/find-a-gym/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//div[@class="club-card cf"]')

    for poi_html in all_locations:
        store_url = poi_html.xpath('.//a[contains(text(), "View More")]/@href')
        store_url = urljoin(start_url, store_url[0]) if store_url else "<MISSING>"
        location_name = poi_html.xpath('.//div[@class="content"]/span[1]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = poi_html.xpath(".//address/span[1]//text()")
        street_address = ", ".join(street_address) if street_address else "<MISSING>"
        city = poi_html.xpath(".//address/span[2]/text()")
        city = city[0] if city else "<MISSING>"
        state = "<MISSING>"
        zip_code = poi_html.xpath(".//address/span[3]/text()")
        zip_code = zip_code[0] if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = poi_html.xpath('.//span[@class="gym-phone text-teal"]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi_html.xpath("@data-lat")[0]
        longitude = poi_html.xpath("@data-lng")[0]

        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        hoo = loc_dom.xpath('.//dl[@class="d-flex upper mb-20 times"]//text()')
        hoo = [elem.strip() for elem in hoo if elem.strip()]
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
