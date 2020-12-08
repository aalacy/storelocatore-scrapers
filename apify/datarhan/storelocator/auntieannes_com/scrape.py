import csv
import json
import urllib.parse
from lxml import etree
from sglogging import SgLogSetup

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("auntieannes_com")


def write_output(data):
    logger.info(f"writing {len(data)} rows to data.csv")
    with open("data.csv", mode="w", newline="", encoding="utf-8") as output_file:
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

    DOMAIN = "auntieannes.com"
    user_agent = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36"
    }

    start_url = "https://auntieannes.com/"
    response = session.get(start_url, headers=user_agent)
    dom = etree.HTML(response.text)
    all_cities = dom.xpath('//select[@id="citySelect"]/option/@value')
    for city_url in all_cities[0:50]:
        logger.info(f"scraping city: {city_url}")
        full_city_url = urllib.parse.urljoin(start_url, city_url)
        city_response = session.get(full_city_url, headers=user_agent)
        city_dom = etree.HTML(city_response.text)

        all_poi_data = city_dom.xpath('//div[@class="city-list"]/ul/li')
        for poi_data in all_poi_data:
            store_url = poi_data.xpath('.//a[@class="generic-link"]/@href')[0]
            store_url = urllib.parse.urljoin(start_url, store_url)
            location_name = poi_data.xpath('.//a[@class="generic-link"]/text()')[0]
            location_name = str(location_name) if location_name else "<MISSING>"
            if "temporarily closed" in location_name.lower():
                continue
            street_address = poi_data.xpath(
                './/div[@class="city-details"]/span[1]/text()'
            )
            street_address = str(street_address[0]) if street_address else "<MISSING>"
            city = poi_data.xpath('.//div[@class="city-details"]/span[2]/text()')
            city = city[0].split(",")[0] if city else "<MISSING>"
            state = poi_data.xpath('.//div[@class="city-details"]/span[2]/text()')
            state = state[0].split(",")[-1].strip().split()[0] if state else "<MISSING>"
            zip_code = poi_data.xpath('.//div[@class="city-details"]/span[2]/text()')
            zip_code = (
                zip_code[0].split(",")[-1].strip().split()[-1]
                if zip_code
                else "<MISSING>"
            )
            country_code = "<MISSING>"
            country_code = country_code if country_code else "<MISSING>"
            store_number = store_url.split("/")[-1]
            phone = poi_data.xpath('//a[@aria-label="Telephone Number"]/span/text()')
            phone = str(phone[0]) if phone else "<MISSING>"

            store_response = session.get(store_url, headers=user_agent)
            store_dom = etree.HTML(store_response.text)
            location_type = "<MISSING>"
            if "food truck" in location_name.lower():
                location_type = "Food Truck"
            location_type = location_type if location_type else "<MISSING>"
            latitude = store_dom.xpath("//a/@data-lat")
            latitude = float(latitude[0]) if latitude else "<MISSING>"
            longitude = store_dom.xpath("//a/@data-long")
            longitude = float(longitude[0]) if longitude else "<MISSING>"
            days_list = store_dom.xpath('//div[@class="hours-wrapper"]//dt/text()')
            hours_list = store_dom.xpath('//div[@class="hours-wrapper"]//dd/text()')
            hours_of_operation = list(
                map(lambda d, h: d + " " + h, days_list, hours_list)
            )
            hours_of_operation = ", ".join(hours_of_operation)
            hours_of_operation = (
                hours_of_operation if hours_of_operation.strip() else "<MISSING>"
            )

            if state == city == zip_code == "<MISSING>":
                phone = street_address
                street_address = "<MISSING>"

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

            if location_name not in scraped_items:
                scraped_items.append(location_name)
                items.append(item)

    return items


def scrape():
    data = fetch_data()
    logger.info(f"fetched {len(data)} rows")
    write_output(data)


if __name__ == "__main__":
    scrape()
