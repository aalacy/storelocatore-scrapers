import csv
import urllib.parse
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
    session = SgRequests()

    items = []
    scraped_items = []

    DOMAIN = "ironmountain.com"
    start_url = "https://locations.ironmountain.com/"
    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations_urls = dom.xpath('//div[@class="countries-list-wrap"]//a/@href')
    for location_url in all_locations_urls:
        location_response = session.get(urllib.parse.urljoin(start_url, location_url))
        location_dom = etree.HTML(location_response.text)

        all_points = location_dom.xpath('//ul[@class="map-list"]//a/@href')
        for point_url in all_points:
            point_response = session.get(urllib.parse.urljoin(start_url, point_url))
            point_dom = etree.HTML(point_response.text)

            all_point_locations = point_dom.xpath('//ul[@class="map-list"]/li')
            for point_location in all_point_locations:
                store_url = point_location.xpath(".//a/@href")[0]
                loc_response = session.get(store_url)
                loc_dom = etree.HTML(loc_response.text)

                location_name = point_location.xpath(".//a/text()")[0]
                location_name = location_name.strip() if location_name else "<MISSING>"
                street_address = loc_dom.xpath(
                    '//meta[@property="business:contact_data:street_address"]/@content'
                )
                street_address = street_address[0] if street_address else "<MISSING>"
                city = loc_dom.xpath(
                    '//meta[@property="business:contact_data:locality"]/@content'
                )
                city = city[0] if city else "<MISSING>"
                state = loc_dom.xpath(
                    '//meta[@property="business:contact_data:region"]/@content'
                )
                state = state[0] if state and len(state[0].strip()) > 1 else "<MISSING>"
                zip_code = loc_dom.xpath(
                    '//meta[@property="business:contact_data:postal_code"]/@content'
                )
                zip_code = (
                    zip_code[0] if zip_code and len(zip_code[0]) > 1 else "<MISSING>"
                )
                if zip_code == "00000":
                    zip_code = "<MISSING>"
                country_code = loc_dom.xpath(
                    '//meta[@property="business:contact_data:country_name"]/@content'
                )
                country_code = country_code[0] if country_code else "<MISSING>"
                store_number = loc_response.url.split("/")[-2]
                phone = loc_dom.xpath(
                    '//meta[@property="business:contact_data:phone_number"]/@content'
                )
                phone = phone[0] if phone else "<MISSING>"
                location_type = "<MISSING>"
                latitude = loc_dom.xpath(
                    '//meta[@property="place:location:latitude"]/@content'
                )
                latitude = latitude[0] if latitude else "<MISSING>"
                longitude = loc_dom.xpath(
                    '//meta[@property="place:location:longitude"]/@content'
                )
                longitude = longitude[0] if longitude else "<MISSING>"
                hours_of_operation = "<MISSING>"

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
