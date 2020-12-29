import csv
import json
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
    session = SgRequests().requests_retry_session(retries=1, backoff_factor=0.3)

    items = []

    DOMAIN = "spherion.com"
    start_url = "https://www.spherion.com/job-seekers/our-locations/"
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
    }
    all_locations = []
    response = session.get(start_url, headers=headers)
    dom = etree.HTML(response.text)
    all_dirs = dom.xpath('//div[@class="branch-loc-search-list-btns"]/a/@href')
    for url in all_dirs:
        response = session.get(urljoin(start_url, url))
        dom = etree.HTML(response.text)
        all_locations += dom.xpath('//div[@class="branch-loc-search-address"]/a/@href')

    for url in all_locations:
        store_url = urljoin(start_url, url)
        if "spherion.com" not in store_url:
            continue
        loc_response = session.get(store_url, headers=headers)
        loc_dom = etree.HTML(loc_response.text)
        store_data = loc_dom.xpath(
            '//script[@type="application/ld+json" and contains(text(), "address")]/text()'
        )
        if not store_data:
            store_data = loc_response.text.split('application/ld+json">')[-1].split(
                "</script>"
            )
        store_data = json.loads(store_data[0])

        location_name = store_data["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = store_data["address"]["streetAddress"]
        street_address = street_address if street_address else "<MISSING>"
        city = store_data["address"]["addressLocality"]
        city = city if city else "<MISSING>"
        state = store_data["address"]["addressRegion"]
        state = state if state else "<MISSING>"
        zip_code = store_data["address"]["postalCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = store_data["address"]["addressCountry"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = "<MISSING>"
        phone = store_data["address"]["telephone"]
        phone = phone if phone else "<MISSING>"
        location_type = store_data["@type"]
        location_type = location_type if location_type else "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = loc_dom.xpath(
            '//div[@class="branch-loc-details--opening-hours"]//text()'
        )
        hours_of_operation = [
            elem.strip() for elem in hours_of_operation if elem.strip()
        ]
        if hours_of_operation:
            hours_of_operation = " ".join(hours_of_operation[1:]).strip()
            if not hours_of_operation.strip():
                hours_of_operation = "<MISSING>"
        else:
            hours_of_operation = "<MISSING>"
        hours_of_operation = hours_of_operation.split("with")[0]
        if hours_of_operation == "<MISSING>":
            hours_of_operation = loc_dom.xpath(
                '//div[@id="ctl08_ctl03_OpeningHoursWrapperDiv"]/p[1]/text()'
            )
            hours_of_operation = hours_of_operation[0] if hours_of_operation else ""
        hours_of_operation = hours_of_operation if hours_of_operation else "<MISSING>"

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
