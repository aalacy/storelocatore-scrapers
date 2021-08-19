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
    session = SgRequests().requests_retry_session(retries=0, backoff_factor=0.3)

    items = []
    scraped_items = []

    DOMAIN = "wrapitup.co.uk"
    start_url = "https://www.wrapitup.co.uk/locations/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//div[@class="eut-element eut-align-left tocenter"]/a/@href'
    )
    for store_url in all_locations:
        if "#" in store_url:
            break
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//h2[@class="dc-loctitle"]/text()')[0].split(
            "! "
        )[-1]
        street_address = " ".join(
            loc_dom.xpath('//span[@itemprop="streetAddress"]/text()')
        )
        city = loc_dom.xpath('//span[@itemprop="addressLocality"]/text()')[0]
        state = "<MISSING>"
        zip_code = loc_dom.xpath('//span[@itemprop="postalCode"]/text()')[0]
        country_code = "UK"
        store_number = "<MISSING>"
        phone = loc_dom.xpath('//a[@title="Contact Number"]/span/text()')
        phone = phone[0] if phone else "<MISSING>"
        if "TBC" in phone:
            phone = "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = loc_dom.xpath('//time[@itemprop="openingHours"]/text()')[
            0
        ].replace("\n", "")

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
        if street_address not in scraped_items:
            scraped_items.append(street_address)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
