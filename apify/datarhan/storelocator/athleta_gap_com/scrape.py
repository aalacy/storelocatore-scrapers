import csv
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
    scraped_items = []

    DOMAIN = "gap.com"
    start_url = "https://athleta.gap.com/stores"

    all_cities = []
    all_locations = []
    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_states = dom.xpath('//div[@class="map-list-item is-single"]/a/@href')
    for state_url in all_states:
        state_response = session.get("https://athleta.gap.com" + state_url)
        state_dom = etree.HTML(state_response.text)
        all_cities += state_dom.xpath("//a[@data-city-item]/@href")

    for city_url in all_cities:
        city_response = session.get("https://athleta.gap.com" + city_url)
        city_dom = etree.HTML(city_response.text)
        all_locations += city_dom.xpath('//li[@role="listitem"]')

    for poi_html in all_locations:
        store_url = poi_html.xpath('.//a[@class="ga-link"]/@href')[0]
        store_url = "https://athleta.gap.com" + store_url
        location_name = poi_html.xpath('.//div[@class="location-name mb-5"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = poi_html.xpath('.//div[@class="address"]/div[1]/text()')
        street_address = street_address[0] if street_address else "<MISSING>"
        city = poi_html.xpath('.//div[@class="address"]/div[2]/text()')
        city = city[0].split(",")[0] if city else "<MISSING>"
        state = poi_html.xpath('.//div[@class="address"]/div[2]/text()')
        state = state[0].split(",")[-1].split()[0] if state else "<MISSING>"
        zip_code = poi_html.xpath('.//div[@class="address"]/div[2]/text()')
        zip_code = zip_code[0].split(",")[-1].split()[-1] if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = poi_html.xpath("@data-lid")
        store_number = store_number[0] if store_number else "<MISSING>"
        phone = poi_html.xpath('.//a[@class="phone ga-link"]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = poi_html.xpath('.//span[@class="store-type"]/text()')
        location_type = location_type[0] if location_type else "<MISSING>"
        latitude = poi_html.xpath('.//a[@class="directions ga-link"]/@href')
        latitude = latitude[0].split("=")[-1].split(",")[0] if latitude else "<MISSING>"
        longitude = poi_html.xpath('.//a[@class="directions ga-link"]/@href')
        longitude = (
            longitude[0].split("=")[-1].split(",")[-1] if longitude else "<MISSING>"
        )
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        hours_of_operation = [
            elem.strip()
            for elem in loc_dom.xpath('//div[@class="hours"]//text()')
            if elem.strip()
        ]
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

        if store_number not in scraped_items:
            scraped_items.append(store_number)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
