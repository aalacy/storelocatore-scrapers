import csv
import json
from lxml import etree
from urllib.parse import urljoin

from sgscrape.sgpostal import parse_address_intl
import cfscrape


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
    items = []

    DOMAIN = "ralphlauren.co.uk"
    start_url = "https://www.ralphlauren.co.uk/en/Stores-ShowCities?countryCode=GB"

    scraper = cfscrape.create_scraper()
    response = scraper.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = []
    all_urls = dom.xpath('//div[@class="store-directory-column"]/a')
    for url_html in all_urls:
        url = url_html.xpath("@href")[0]
        scraper = cfscrape.create_scraper()
        response = scraper.get(urljoin(start_url, url))
        dom = etree.HTML(response.text)
        poi_urls = dom.xpath('//span[@class="store-listing-name"]/a/@href')
        if poi_urls:
            all_locations += poi_urls
        else:
            all_locations.append(url)

    for url in all_locations:
        store_url = urljoin(start_url, url)
        scraper = cfscrape.create_scraper()
        loc_response = scraper.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        poi = loc_dom.xpath("//@data-storejson")[0]
        poi = json.loads(poi)[0]

        location_name = loc_dom.xpath('//div[@class="store-locator-details"]/h1/text()')
        location_name = location_name[0].strip() if location_name else "<MISSING>"
        raw_address = loc_dom.xpath('//p[@class="store-address"]/text()')
        raw_address = " ".join(
            [elem.strip().replace("\n", " ") for elem in raw_address if elem.strip()]
        )
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address = addr.street_address_2 + " " + addr.street_address_1
        city = poi["city"]
        state = poi["stateCode"]
        state = state if state else "<MISSING>"
        zip_code = poi["postalCode"]
        country_code = poi["countryCode"]
        store_number = "<MISSING>"
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["latitude"]
        longitude = poi["longitude"]
        hoo = loc_dom.xpath('//td[@class="store-hours-day"]/text()')
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

        items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
