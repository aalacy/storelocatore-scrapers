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

    start_url = "https://drpilatesla.com/"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    store_url = start_url
    location_name = dom.xpath(
        '//h1[contains(text(), "Location")]/following-sibling::div[2]//h2/text()'
    )
    location_name = location_name[0] if location_name else "<MISSING>"
    street_address = dom.xpath(
        '//h1[contains(text(), "Location")]/following-sibling::div[2]/div[1]/span[2]/text()'
    )
    street_address = street_address[0] if street_address else "<MISSING>"
    city = dom.xpath(
        '//h1[contains(text(), "Location")]/following-sibling::div[2]/div[1]/span[3]/text()'
    )[0].split(", ")[0]
    state = dom.xpath(
        '//h1[contains(text(), "Location")]/following-sibling::div[2]/div[1]/span[3]/text()'
    )[0].split(", ")[-1]
    zip_code = dom.xpath(
        '//h1[contains(text(), "Location")]/following-sibling::div[2]/div[1]/span[4]/text()'
    )
    zip_code = zip_code[0] if zip_code else "<MISSING>"
    country_code = "<MISSING>"
    store_number = "<MISSING>"
    phone = dom.xpath(
        '//h1[contains(text(), "Location")]/following-sibling::div[2]/div[1]/span[1]/a/text()'
    )[0]
    location_type = "<MISSING>"
    geo = (
        dom.xpath('//a[contains(@href, "/maps/")]/@href')[0]
        .split("/@")[-1]
        .split(",")[:2]
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
