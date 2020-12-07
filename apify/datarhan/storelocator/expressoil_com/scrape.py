import csv
import json
from lxml import etree
from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w") as output_file:
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

    DOMAIN = "expressoil.com"
    start_url = "https://www.expressoil.com/stores/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//div[@class="location-store"]')

    for poi_html in all_locations:
        store_url = poi_html.xpath("@data-viewurl")
        store_url = store_url[0] if store_url else "<MISSING>"
        store_response = session.get(store_url)
        store_dom = etree.HTML(store_response.text)
        store_data = store_dom.xpath('//script[@type="application/ld+json"]/text()')
        store_data = json.loads(store_data[0].replace("\n", ""))
        if type(store_data) == dict:
            store_data = [
                store_data,
            ]

        location_name = store_data[0]["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = store_data[0]["address"]["streetAddress"]
        street_address = street_address if street_address else "<MISSING>"
        city = store_data[0]["address"]["addressLocality"]
        city = city if city else "<MISSING>"
        state = store_data[0]["address"]["addressRegion"]
        state = state if state else "<MISSING>"
        zip_code = store_data[0]["address"]["postalCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = store_data[0]["address"]["addressCountry"]
        store_number = poi_html.xpath('.//div[@class="location-cta"]/a/@href')
        store_number = store_number[0].split("=")[-1] if store_number else "<MISSING>"
        if "/" in store_number:
            store_number = store_number.split("/")[-2]
        phone = store_data[0].get("telephone")
        phone = phone if phone else "<MISSING>"
        location_type = store_data[0]["@type"]
        location_type = location_type if location_type else "<MISSING>"
        latitude = poi_html.xpath("@data-latitude")
        latitude = latitude[0] if latitude else "<MISSING>"
        longitude = poi_html.xpath("@data-longitude")
        longitude = longitude[0] if longitude else "<MISSING>"
        hours_of_operation = store_dom.xpath('//h5[span[@clas="location-hrs"]]//text()')
        hours_of_operation = [
            elem.strip() for elem in hours_of_operation if elem.strip()
        ]
        hours_of_operation = (
            " ".join(hours_of_operation[1:]) if hours_of_operation else "<MISSING>"
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
