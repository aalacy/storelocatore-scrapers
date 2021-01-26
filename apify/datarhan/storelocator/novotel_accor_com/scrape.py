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
    session = SgRequests()

    DOMAIN = "nothingbundtcakes.com"

    items = []

    start_url = "https://novotel.accor.com/gb/world/hotels-novotel-monde.shtml"

    all_locations = []
    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_cities = dom.xpath('//div[@class="select_destination_bloc"]/a/@href')
    for url in all_cities:
        response = session.get(urljoin(start_url, url))
        dom = etree.HTML(response.text)
        all_locations += dom.xpath("//div[@data-rid]//h3/a/@href")
        next_page = dom.xpath('//a[contains(text(), ">")]/@href')
        while next_page:
            response = session.get(urljoin(start_url, next_page[0]))
            dom = etree.HTML(response.text)
            all_locations += dom.xpath("//div[@data-rid]//h3/a/@href")
            next_page = dom.xpath('//a[contains(text(), ">")]/@href')

    for url in list(set(all_locations)):
        poi_url = urljoin(start_url, url)
        loc_response = session.get(poi_url)
        loc_dom = etree.HTML(loc_response.text)
        poi = loc_dom.xpath(
            '//script[@type="application/ld+json" and contains(text(), "telephone")]/text()'
        )
        if not poi:
            continue
        poi = json.loads(poi[0])

        poi_name = poi["name"]
        poi_name = poi_name if poi_name else "<MISSING>"
        street = loc_dom.xpath('//meta[@property="og:street-address"]/@content')
        street = street[0] if street else "<MISSING>"
        city = poi["address"]["addressLocality"]
        city = city if city else "<MISSING>"
        state = "<MISSING>"
        zip_code = poi["address"].get("postalCode")
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["address"]["addressCountry"]
        country_code = country_code if country_code else "<MISSING>"
        if country_code not in ["UNITED KINGDOM", "CANADA"]:
            continue
        poi_number = "<MISSING>"
        phone = poi["telephone"]
        poi_type = poi["@type"]
        latitude = loc_dom.xpath('//meta[@property="og:latitude"]/@content')[0]
        longitude = loc_dom.xpath('//meta[@property="og:longitude"]/@content')[0]
        hoo = "<MISSING>"

        item = [
            DOMAIN,
            poi_url,
            poi_name,
            street,
            city,
            state,
            zip_code,
            country_code,
            poi_number,
            phone,
            poi_type,
            latitude,
            longitude,
            hoo,
        ]
        items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
