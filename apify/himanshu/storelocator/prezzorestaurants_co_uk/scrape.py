import re
import csv
from lxml import etree
from urllib.parse import urljoin

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

    start_url = "https://www.prezzorestaurants.co.uk/find-and-book/search/?s=london&lng=-0.1277583&lat=51.5073509&f=&of=0&command=book&dist=5000&p=1&X-Requested-With=XMLHttpRequest"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//a[contains(text(), "View restaurant")]/@href')
    next_page = dom.xpath("//a/@data-load")
    while next_page:
        response = session.get(next_page[0], headers=hdr)
        dom = etree.HTML(response.text)
        all_locations += dom.xpath('//a[contains(text(), "View restaurant")]/@href')
        next_page = dom.xpath("//a/@data-load")

    for url in all_locations:
        store_url = urljoin(start_url, url)
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath(
            '//h2[@class="title mb-2 has-text-weight-bold"]/text()'
        )
        location_name = location_name[0].strip() if location_name else "<MISSING>"
        raw_address = loc_dom.xpath(
            '//h4[a[contains(@href, "tel")]]/following-sibling::div[1]/p[1]/text()'
        )
        raw_address = [" ".join(e.split()) for e in raw_address][0]
        addr = parse_address_intl(raw_address)
        street_address = ", ".join(raw_address.split(", ")[:-2])
        city = addr.city
        city = city if city else "<MISSING>"
        if city in street_address:
            street_address = street_address.split(f", {city}")[0]
        state = addr.state
        state = state if state else "<MISSING>"
        zip_code = addr.postcode
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = addr.country
        country_code = country_code if country_code else "<MISSING>"
        store_number = "<MISSING>"
        phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        if "/@" in loc_dom.xpath('//a[contains(@href, "maps")]/@href')[0]:
            geo = (
                loc_dom.xpath('//a[contains(@href, "maps")]/@href')[0]
                .split("/@")[-1]
                .split(",")[:2]
            )
            latitude = geo[0]
            longitude = geo[1]

        loc_response = session.get(store_url + "?X-Requested-With=XMLHttpRequest")
        hoo = loc_dom.xpath(
            '//div[h4[contains(text(), "Opening times")]]/following-sibling::div//text()'
        )
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

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
