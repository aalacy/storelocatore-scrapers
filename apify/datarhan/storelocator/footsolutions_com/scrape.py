import csv
from lxml import etree
from time import sleep
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgselenium import SgFirefox


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
        loc_response = session.get(store_url, headers=hdr)
        if loc_response.status_code == 404:
            continue
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//h3[contains(@class, "StoreDetails")]/text()')
        if location_name:
            location_name = location_name[0]
            street_address = loc_dom.xpath(
                '//p[contains(@class, "StreetAddress")]/text()'
            )[0]
            city = loc_dom.xpath('//p[contains(@class, "__Address")]/text()')[0].split(
                ", "
            )[0]
            if (
                len(
                    loc_dom.xpath('//p[contains(@class, "__Address")]/text()')[0]
                    .split(", ")[-1]
                    .split()[-1]
                )
                == 3
            ):
                state = (
                    loc_dom.xpath('//p[contains(@class, "__Address")]/text()')[0]
                    .split(", ")[-1]
                    .split()[0]
                )
                zip_code = (
                    loc_dom.xpath('//p[contains(@class, "__Address")]/text()')[0]
                    .split(", ")[-1]
                    .split()[1:]
                )
                zip_code = " ".join(zip_code)
            else:
                state = " ".join(
                    loc_dom.xpath('//p[contains(@class, "__Address")]/text()')[0]
                    .split(", ")[-1]
                    .split()[:-1]
                )
                zip_code = (
                    loc_dom.xpath('//p[contains(@class, "__Address")]/text()')[0]
                    .split(", ")[-1]
                    .split()[-1]
                )
            if zip_code in street_address:
                street_address = street_address.split(",")[0]
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            country_code = "<MISSING>"
            store_number = "<MISSING>"
            phone = loc_dom.xpath('//p[contains(@class, "Phone")]/text()')
            phone = phone[0] if phone else "<MISSING>"
            location_type = "<MISSING>"
            hours_of_operation = loc_dom.xpath(
                '//div[contains(@class, "HourBlock")]/p/text()'
            )
            hours_of_operation = (
                " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
            )
        else:
            location_name = loc_dom.xpath(
                '//h2[contains(@class, "Hero__SubTitle")]/text()'
            )
            location_name = location_name[0] if location_name else "<MISSING>"
            raw_address = loc_dom.xpath('//a[contains(@href, "maps.google")]/p/text()')
            raw_address = [
                e.strip() for e in raw_address if e.strip() and e.strip() != ","
            ]
            street_address = raw_address[0]
            city = raw_address[1]
            state = raw_address[2]
            zip_code = raw_address[-1]
            country_code = "<MISSING>"
            store_number = "<MISSING>"
            phone = loc_dom.xpath('//a[contains(@class, "Hero__Phone")]/text()')
            phone = phone[0] if phone else "<MISSING>"
            location_type = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            hoo = loc_dom.xpath(
                '//p[contains(text(), "Hours")]/following-sibling::p/text()'
            )
            hoo = [e.strip() for e in hoo if e.strip()]
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
