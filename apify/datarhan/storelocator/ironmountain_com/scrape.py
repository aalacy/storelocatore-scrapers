import re
import csv
import demjson
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
            for point_num, point_location in enumerate(all_point_locations):
                store_url = point_location.xpath(".//a/@href")[0]
                location_name = point_location.xpath(
                    './/span[@class="location-name capitalize bold text-blue"]/text()'
                )[0]
                location_name = location_name.strip() if location_name else "<MISSING>"
                street_address = point_location.xpath(
                    ".//div[@data-hide-address]/text()"
                )[0]
                street_address = street_address if street_address else "<MISSING>"
                raw_adr_data = point_location.xpath(
                    './/div[@class="country-name"]/preceding-sibling::div[1]/text()'
                )[0]
                city = raw_adr_data.split(",")[0]
                city = city.strip() if city else "<MISSING>"
                state = raw_adr_data.split(",")[-1].strip().split()[0]
                state = state.strip() if state else "<MISSING>"
                street_address = street_address.replace(state, "").strip()
                zip_code = raw_adr_data.split(",")[-1].strip().split()[1:]
                zip_code = " ".join(zip_code).strip() if zip_code else "<MISSING>"
                country_code = point_location.xpath(
                    './/div[@class="country-name"]/@data-show-uk'
                )[0]
                country_code = country_code if country_code else "<MISSING>"
                store_number = point_location.xpath("@data-fid")[0]
                phone = point_location.xpath(
                    './/div[@class="phone italic font-sm mb-10"]/@data-hide-empty'
                )[0]
                phone = phone if phone else "<MISSING>"
                location_type = "<MISSING>"

                geo_data = re.findall(
                    "RLS.defaultData =(.+);",
                    etree.tostring(point_dom.xpath('//div[@id="gmap"]')[0])
                    .decode("utf-8")
                    .replace("\n", ""),
                )[0]
                geo_data = demjson.decode(geo_data)
                point_geo_data = geo_data["markerData"][point_num]
                latitude = point_geo_data["lat"]
                latitude = latitude if latitude else "<MISSING>"
                longitude = point_geo_data["lng"]
                longitude = longitude if longitude else "<MISSING>"

                hours_of_operation = ""
                hours_of_operation = (
                    hours_of_operation if hours_of_operation else "<MISSING>"
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
