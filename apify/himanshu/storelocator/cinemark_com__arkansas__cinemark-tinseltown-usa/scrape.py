import re
import csv
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl


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

    store_url = "https://cinemark.com/theatres/ar-benton/cinemark-tinseltown-usa"
    domain = re.findall("://(.+?)/", store_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(store_url, headers=hdr)
    dom = etree.HTML(response.text)

    location_name = dom.xpath('//h1[@class="theatreName"]/text()')
    location_name = location_name[0] if location_name else "<MISSING>"
    addr = parse_address_intl(
        dom.xpath('//div[@class="addressBody"]/text()')[0].strip()
    )
    street_address = addr.street_address_1
    if addr.street_address_2:
        street_address += " " + addr.street_address_2
    street_address = street_address if street_address else "<MISSING>"
    city = addr.city
    city = city if city else "<MISSING>"
    state = addr.state
    state = state if state else "<MISSING>"
    zip_code = addr.postcode
    zip_code = zip_code if zip_code else "<MISSING>"
    country_code = addr.country
    country_code = country_code if country_code else "<MISSING>"
    store_number = "<MISSING>"
    phone = dom.xpath('//div[svg[@aria-labelledby="icon-title-phone"]]/text()')
    phone = phone[1].strip() if phone else "<MISSING>"
    location_type = "<MISSING>"
    geo = (
        dom.xpath('//div[@class="theatreMap"]//img/@data-src')[0]
        .split("Road/")[-1]
        .split("/")[0]
        .split(",")
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
