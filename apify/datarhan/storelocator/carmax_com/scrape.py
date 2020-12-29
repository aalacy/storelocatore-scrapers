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
    session = SgRequests().requests_retry_session(retries=0, backoff_factor=0.3)

    items = []

    DOMAIN = "carmax.com"
    start_url = "https://www.carmax.com/stores"

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
    }
    response = session.get(start_url, headers=headers)
    dom = etree.HTML(response.text)

    all_locations = []
    all_states = dom.xpath('//li[@class="stores-list-cabinet"]/a/@href')
    for state_url in all_states:
        state_url = "https://www.carmax.com" + state_url
        state_response = session.get(state_url, headers=headers)
        state_dom = etree.HTML(state_response.text)
        urls = state_dom.xpath('//a[@class="stores-list-cabinet--single"]/@href')
        loc_urls = state_dom.xpath('//a[contains(@id, "store-details")]/@href')
        all_locations += loc_urls
        for url in urls:
            if (url.split("/")[-1]).isdigit():
                all_locations.append(url)

    for url in list(set(all_locations)):
        store_url = "https://www.carmax.com" + url
        store_response = session.get(store_url, headers=headers)
        store_dom = etree.HTML(store_response.text)
        store_data = store_dom.xpath(
            '//script[@type="application/ld+json" and contains(text(), "GeoCoordinates")]/text()'
        )[0]
        store_data = json.loads(store_data)
        location_name = store_dom.xpath('//h1[@id="main-content-heading"]//text()')
        location_name = [elem.strip() for elem in location_name if elem.strip()]
        location_name = " ".join(location_name) if location_name else "<MISSING>"
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
        store_number = store_data["id"]
        store_number = store_number if store_number else "<MISSING>"
        phone = store_data["telephone"]
        phone = phone if phone else "<MISSING>"
        location_type = store_data["@type"]
        location_type = location_type if location_type else "<MISSING>"
        latitude = store_data["geo"]["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = store_data["geo"]["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = []
        for elem in store_data["openingHoursSpecification"]:
            day = elem["dayOfWeek"].split("/")[-1]
            opens = elem["opens"]
            closes = elem["closes"]
            hours_of_operation.append("{}  {} - {}".format(day, opens, closes))
        hours_of_operation = (
            " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
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
