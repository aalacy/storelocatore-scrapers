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
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []

    start_url = "https://goldenstartheaters.com/"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//ul[@id="menu-main-navbar"]//a[contains(text(), "Theaters")]/following-sibling::ul//a/@href'
    )
    for store_url in all_locations:
        if "goldenstartheaters" not in store_url:
            continue
        loc_response = session.get(store_url, headers=hdr)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath(
            '//h2[@class="elementor-heading-title elementor-size-default"]/text()'
        )[0]
        raw_address = loc_dom.xpath('//a[contains(@href, "maps?")]/@href')
        if raw_address:
            raw_address = (
                raw_address[0].split("?q=")[-1].split("&um")[0].replace("+", " ")
            )
        else:
            raw_address = (
                loc_dom.xpath('//*[a[contains(@href, "maps")]]//text()')[0]
                .split("|")[0]
                .strip()
            )
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        city = addr.city
        state = addr.state
        zip_code = addr.postcode
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = loc_dom.xpath('//a[contains(@href, "maps")]/following::text()')[0]
        if phone and phone.strip():
            phone = (
                phone.split("Phone:")[-1]
                .strip()
                .replace("\u202d", "")
                .split("Showtimes")[0]
                .strip()
            )
        else:
            phone = (
                loc_dom.xpath(
                    '//a[contains(@href, "maps")]/following-sibling::span/text()'
                )[0]
                .split("Phone: ")[-1]
                .split("Showtimes")[0]
                .strip()
            )
        location_type = "<MISSING>"
        geo = loc_dom.xpath('//a[contains(@href, "maps")]/@href')[0]
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        if "@" in geo:
            geo = geo.split("/@")[-1].split(",")[:2]
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
