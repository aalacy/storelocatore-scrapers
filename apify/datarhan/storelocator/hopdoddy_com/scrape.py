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

    items = []
    scraped_items = []

    DOMAIN = "hopdoddy.com"
    start_url = "https://www.hopdoddy.com/locations"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath(
        '//a[@class="alllocations__buttondetails w-inline-block"]/@href'
    )

    for url in all_locations:
        poi_url = urljoin(start_url, url)
        loc_response = session.get(poi_url)
        loc_dom = etree.HTML(loc_response.text)
        poi = loc_dom.xpath('//script[@type="application/ld+json"]/text()')[0]
        poi = json.loads(poi)

        poi_name = poi["name"]
        street = poi["address"]["streetAddress"]
        street = street if street else "<MISSING>"
        city = poi["address"]["addressLocality"]
        city = city if city else "<MISSING>"
        state = poi["address"]["addressRegion"]
        state = state if state else "<MISSING>"
        zip_code = poi["address"]["postalCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["address"]["addressCountry"]
        country_code = country_code if country_code else "<MISSING>"
        poi_number = loc_dom.xpath("//@data-location-olo-id")[0]
        phone = poi["telephone"]
        phone = phone if phone else "<MISSING>"
        poi_type = poi["@type"]
        geo = (
            loc_dom.xpath('//iframe[contains(@src, "maps")]/@src')[0]
            .split("1d")[-1]
            .split("!3")[0]
            .split("!2d")
        )
        latitude = geo[0]
        longitude = geo[1]

        hours_of_operation = []
        hoo_response = session.get(
            "https://na6c0i4fb0.execute-api.us-west-2.amazonaws.com/calendars/{}".format(
                poi_number
            )
        )
        hoo = json.loads(hoo_response.text)
        for elem in hoo["data"]:
            hours_of_operation.append(f'{elem["day"]} {elem["opens"]} {elem["closes"]}')
        hoo = " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"

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
        check = f"{poi_name} {street}"
        if check not in scraped_items:
            scraped_items.append(check)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
