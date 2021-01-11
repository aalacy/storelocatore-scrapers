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
    session = SgRequests()

    items = []

    DOMAIN = "honest-1.com"
    start_url = "https://www.honest-1.com/api/json/places/get"

    response = session.get(start_url)
    data = json.loads(response.text)

    for poi in data["places"]["locations"]:
        poi_name = poi["entry"]["title"]
        poi_url = poi["contacts"]["url"]
        street = poi["postalAddress"]["street"]
        street = street if street else "<MISSING>"
        city = poi["postalAddress"]["city"]
        city = city if city else "<MISSING>"
        state = poi["postalAddress"]["region"]
        state = state if state else "<MISSING>"
        zip_code = poi["postalAddress"]["code"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["postalAddress"]["country"]
        country_code = country_code if country_code else "<MISSING>"
        poi_number = "<MISSING>"
        phone = poi["contacts"]["phone"]
        phone = phone if phone else "<MISSING>"
        poi_type = "<MISSING>"
        latitude = poi["geoLocation"]["lat"]
        longitude = poi["geoLocation"]["lng"]

        loc_response = session.get(poi_url)
        loc_dom = etree.HTML(loc_response.text)

        hoo = loc_dom.xpath('//div[@class="header-worktime"]//text()')
        if not hoo:
            hoo = loc_dom.xpath('//span[contains(text(), "am -")]/text()')[:2]
        hoo = " ".join(hoo) if hoo else "<MISSING>"
        city = loc_dom.xpath('//meta[@itemprop="addressLocality"]/@content')
        city = city[0] if city else poi["postalAddress"]["city"]

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
