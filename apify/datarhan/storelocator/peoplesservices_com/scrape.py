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

    start_url = "https://www.peoplesservices.com/locations/"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    all_locations = []
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    states_urls = dom.xpath(
        '//h3[contains(text(), "Expertise in Warehousing and Logistics")]/following-sibling::h2//a/@href'
    )
    for url in states_urls:
        response = session.get(urljoin(start_url, url))
        dom = etree.HTML(response.text)
        all_locations += dom.xpath(
            '//h2[@class="vc_custom_heading location-table-heading"]/following-sibling::div[@class="vc_row wpb_row vc_inner vc_row-fluid"]'
        )

    for poi_html in all_locations:
        store_url = start_url
        location_name = poi_html.xpath(
            './/div[@class="wpb_text_column wpb_content_element "]//strong/text()'
        )
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_address = poi_html.xpath(
            './/div[@class="wpb_text_column wpb_content_element "]/div[1]/p[1]/text()'
        )[:2]
        raw_address = [e.strip() for e in raw_address]
        if "Main Office" in raw_address[0]:
            raw_address = poi_html.xpath(
                './/div[@class="wpb_text_column wpb_content_element "]/div[1]/p[1]/text()'
            )[1:3]
        street_address = raw_address[0].strip()
        city = raw_address[1].split(", ")[0].strip()
        state = raw_address[1].split(", ")[-1].split()[0].strip()
        zip_code = raw_address[1].split(", ")[-1].split()[-1].strip()
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = (
            poi_html.xpath(
                './/div[@class="wpb_text_column wpb_content_element "]/div[1]/p[1]/text()'
            )[2]
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
