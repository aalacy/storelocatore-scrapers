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
    scraped_items = []

    DOMAIN = "footsolutions.com"
    start_url = "https://footsolutions.com/map"

    hdr = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//a[contains(@class, "Map__StoreLink")]/@href')

    for url in list(set(all_locations)):
        store_url = urljoin(start_url, url)
        if store_url == "https://footsolutions.com/sandy-springs":
            store_url = "https://footsolutions.com/sandysprings"
        loc_response = session.get(store_url, headers=hdr)
        if loc_response.status_code == 404:
            continue
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//h2[contains(@class, "Hero__SubTitle")]/text()')
        if not location_name:
            location_name = loc_dom.xpath(
                '//h1[contains(@class, "Headings__TitleM")]/text()'
            )
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_address = loc_dom.xpath('//a[contains(@href, "maps.google")]/p/text()')
        raw_address = [e.strip() for e in raw_address if e.strip()]
        addr = parse_address_intl(" ".join(raw_address))
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        if not street_address:
            street_address = raw_address[0]
        if street_address.endswith("/"):
            street_address = street_address[:-1]
        city = addr.city
        if not city:
            city = raw_address[1].split(", ")[0]
        city = city.split("/")[0].strip()
        state = addr.state
        if not state:
            state = raw_address[1].split(", ")[-1].split()[0]
        zip_code = addr.postcode
        if not zip_code:
            zip_code = raw_address[1].split(", ")[-1].split()[-1]
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = loc_dom.xpath('//a[contains(@class, "Hero__Phone")]/text()')
        if not phone:
            phone = loc_dom.xpath('//p[contains(@class, "Phone")]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hoo = loc_dom.xpath(
            '//p[contains(text(), "Hours")]/following-sibling::p/text()'
        )
        if not hoo:
            hoo = loc_dom.xpath(
                '//h1[contains(text(), "Hours")]/following-sibling::div/p/text()'
            )
        hoo = [
            " - ".join(
                [s.strip() for s in e.strip().split("-") if "april" not in s.lower()]
            )
            for e in hoo
            if e.strip()
        ]
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"
        if "Private Appointments" in hours_of_operation:
            hours_of_operation = "10:00AM - 05:00PM"

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
        check = f"{location_name} {street_address}"
        if check not in scraped_items:
            scraped_items.append(check)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
