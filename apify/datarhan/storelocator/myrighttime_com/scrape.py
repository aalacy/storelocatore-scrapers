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

    DOMAIN = "myrighttime.com"
    start_url = "https://www.myrighttime.com/locations"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//div[@id="pm2020"]//p/a/@href')
    all_locations += dom.xpath('//div[@id="pm2021"]//p/a/@href')
    all_locations += dom.xpath('//div[@id="pm2022"]//p/a/@href')

    for url in all_locations:
        store_url = urljoin(start_url, url)
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        raw_address = loc_dom.xpath('//a[contains(@href, "g.page")]//text()')
        if not raw_address:
            raw_address = loc_dom.xpath('//a[contains(@href, ".gl/")]//text()')
        raw_address = [
            elem.strip()
            for elem in raw_address
            if elem.strip() and ("Potomac Woods Plaza" and "The Shops") not in elem
        ]
        location_name = raw_address[-1].split(", ")[0]
        street_address = raw_address[0]
        city = location_name
        state = raw_address[-1].split(", ")[-1].split()[0]
        zip_code = raw_address[-1].split(", ")[-1].split()[-1]
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hoo = loc_dom.xpath('//p[contains(text(), "am - ")]/text()')
        hoo = [elem.strip() for elem in hoo]
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
