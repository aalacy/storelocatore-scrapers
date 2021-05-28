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

    start_url = "https://cinestarz.ca/"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="menu-footer-en-container"]//li/a/@href')
    for store_url in all_locations:
        print(store_url)
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        if loc_dom.xpath('//h3[contains(text(), "TEMPORARILY CLOSED")]'):
            continue

        location_name = loc_dom.xpath('//h2[@class="vc_custom_heading"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_data = loc_dom.xpath(
            '//div[@id="contact"]//div[@class="wpb_wrapper"]/p/text()'
        )
        raw_data = [e.strip() for e in raw_data if e.strip()]
        if not raw_data:
            continue
        street_address = raw_data[0]
        city = raw_data[1].split(", ")[0].strip()
        state = raw_data[1].split(", ")[-1].strip()
        zip_code = raw_data[2].strip()
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = raw_data[-1].split(":")[-1].strip()
        location_type = "<MISSING>"
        geo = (
            loc_dom.xpath("//iframe/@src")[0].split("ll=")[-1].split("&")[0].split(",")
        )
        latitude = geo[0]
        longitude = geo[1]
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
