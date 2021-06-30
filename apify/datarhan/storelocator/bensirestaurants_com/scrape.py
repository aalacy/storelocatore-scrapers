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
    domain = "bensirestaurants.com"

    store_urls = [
        "http://www.bensirestaurants.com/bensi-denville.html",
        "http://www.bensirestaurants.com/bensi-hasbrouck-heights.html",
        "http://www.bensirestaurants.com/bensi-whitehouse-station.html",
        "http://www.bensirestaurants.com/bensi-on-berdan-llc.html",
    ]

    for store_url in store_urls:
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//h2[@class="wsite-content-title"]/font/text()')
        if not location_name:
            location_name = loc_dom.xpath(
                '//div[@class="paragraph"]/font/font/strong/text()'
            )
        if not location_name:
            location_name = loc_dom.xpath(
                '//div[@class="paragraph"]/strong/font/text()'
            )
        location_name = (
            location_name[0].split("-")[0].strip() if location_name else "<MISSING>"
        )
        raw_address = loc_dom.xpath(
            '//h2[@class="wsite-content-title"]/font[2]/span/font/text()'
        )
        if not raw_address:
            raw_address = loc_dom.xpath("//h2/font[1]/text()")
            raw_address = raw_address[1:] if raw_address else ""
        if not raw_address:
            raw_address = loc_dom.xpath('//div[@class="paragraph"]/font[2]/text()')
            raw_address = raw_address[1:]
        if not raw_address:
            raw_1 = loc_dom.xpath('//div[@class="paragraph"]/strong/font/text()')[
                0
            ].split(":")[-1]
            raw_2 = (
                loc_dom.xpath('//div[@class="paragraph"]/strong/font/text()')[1]
                .strip()
                .replace("\u200b", "")
            )
            raw_address = [raw_1 + " " + raw_2]
        raw_address = (
            raw_address[0]
            .split("Address:")[-1]
            .replace(" at Denville Commons.", "")
            .split(", ")
        )
        street_address = raw_address[0].strip()
        city = raw_address[1]
        state = raw_address[-1].split()[0]
        zip_code = raw_address[-1].split()[-1]
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = loc_dom.xpath('//h2[@class="wsite-content-title"]/font/text()')
        phone = (
            phone[0].split("Tel")[-1].strip().split("Call")[-1].strip()
            if phone
            else "<MISSING>"
        )
        if phone == "<MISSING>":
            phone = loc_dom.xpath('//div[@class="paragraph"]/font[2]/text()')
            phone = phone[0].strip() if phone else "<MISSING>"
        if phone == "<MISSING>":
            phone = (
                loc_dom.xpath('//div[@class="paragraph"]/strong/font/text()')[0]
                .split("Tel")[-1]
                .split()[0]
            )
        location_type = "<MISSING>"
        geo = loc_dom.xpath('//a[span[contains(text(), "Direction")]]/@href')[0]
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        if "/@" in geo:
            geo = geo.split("/@")[-1].split(",")[:2]
            latitude = geo[0]
            longitude = geo[1]
        hoo = re.findall("(Open .+? pm)", loc_response.text)
        hours_of_operation = hoo[0] if hoo else "<MISSING>"

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
