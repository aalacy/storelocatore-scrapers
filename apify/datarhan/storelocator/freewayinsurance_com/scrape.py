import re
import csv
import json
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

    DOMAIN = "freewayinsurance.com"
    start_url = "https://www.freewayinsurance.com/office-locator/"
    post_url = "https://www.freewayinsurance.com/office-locator/"

    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    }

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_states = dom.xpath('//select[@id="state"]/option/@value')

    all_locations = []
    for state in all_states[1:]:
        formdata = {
            "search_state": state,
            "page": "1",
            "search": "search",
            "radius": "200",
        }
        state_response = session.post(post_url, data=formdata, headers=headers)
        state_dom = etree.HTML(state_response.text)
        all_locations += state_dom.xpath(
            '//div[@class="office-peek__controls"]/a[2]/@href'
        )

        next_page = state_dom.xpath('//a[@title="Next page"]/@onclick')
        if next_page:
            next_page = re.findall(r"\d+", next_page[0])[0]

            while next_page:
                formdata = {
                    "search_state": state,
                    "page": str(next_page),
                    "search": "search",
                    "radius": "200",
                }
                page_response = session.post(post_url, data=formdata, headers=headers)
                page_dom = etree.HTML(page_response.text)
                all_locations += page_dom.xpath(
                    '//div[@class="office-peek__controls"]/a[2]/@href'
                )
                next_page = page_dom.xpath('//a[@title="Next page"]/@onclick')
                if next_page:
                    if "1" in next_page[0]:
                        next_page = None

    for store_url in all_locations:
        store_response = session.get(store_url)
        store_dom = etree.HTML(store_response.text)
        store_data = store_dom.xpath(
            '//script[@type="application/ld+json" and contains(text(), "address")]/text()'
        )[0]
        store_data = json.loads(store_data.replace("\n", ""))

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
        phone = store_data["telephone"]
        phone = phone if phone else "<MISSING>"
        location_type = store_data["@type"]
        location_type = location_type if location_type else "<MISSING>"
        latitude = store_data["geo"]["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = store_data["geo"]["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = store_data["openingHours"]
        hours_of_operation = (
            ", ".join(hours_of_operation) if hours_of_operation else "<MISSING"
        )

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
