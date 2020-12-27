import csv
import jstyleson
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
    session = SgRequests()

    items = []

    DOMAIN = "underarmour.ca"
    start_url = "http://store-locations.underarmour.com/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = []
    states_urls = dom.xpath(
        '//h3[contains(text(), "Canada")]/following-sibling::ul//a/@href'
    )
    for url in states_urls:
        state_response = session.get(url)
        state_dom = etree.HTML(state_response.text)
        cities_urls = state_dom.xpath('//a[@linktrack="State index"]/@href')
        for c_url in cities_urls:
            city_response = session.get(c_url)
            city_dom = etree.HTML(city_response.text)
            all_locations += city_dom.xpath(
                '//a[@data-gaact="Click_to_Store_Details"]/@href'
            )

    for url in list(set(all_locations)):
        loc_response = session.get(url)
        loc_dom = etree.HTML(loc_response.text)
        store_data = loc_dom.xpath(
            '//script[@type="application/ld+json" and contains(text(), "streetAddress")]/text()'
        )
        poi = jstyleson.loads(store_data[0])

        store_url = url
        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["address"]["streetAddress"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["address"]["addressLocality"]
        city = city if city else "<MISSING>"
        state = poi["address"]["addressRegion"]
        state = state if state else "<MISSING>"
        zip_code = poi["address"]["postalCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["address"]["addressCountry"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["@id"]
        store_number = store_number if store_number else "<MISSING>"
        phone = poi["telephone"]
        if phone:
            phone = phone if phone != "#" else ""
        phone = phone if phone else "<MISSING>"
        location_type = poi["@type"]
        location_type = location_type if location_type else "<MISSING>"
        latitude = poi["geo"]["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["geo"]["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = []
        for elem in poi["openingHoursSpecification"]:
            day = elem["dayOfWeek"][0]
            opens = elem["opens"]
            closes = elem["closes"]
            hours_of_operation.append(f"{day} {opens} - {closes}")
        hours_of_operation = (
            ", ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
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
