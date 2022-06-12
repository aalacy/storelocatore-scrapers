import re
import csv
import json
from lxml import etree

from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


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
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []
    scraped_items = []

    start_url = "https://www.bouclair.com/on/demandware.store/Sites-bouclair-Site/en/Stores-FindStores?lat={}&long={}"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")

    all_locations = []
    all_coordinates = DynamicGeoSearch(
        country_codes=[SearchableCountries.CANADA], max_radius_miles=100
    )
    for lat, lng in all_coordinates:
        response = session.get(start_url.format(lat, lng))
        data = json.loads(response.text)
        all_locations += data["stores"]

    for poi in all_locations:
        poi_html = etree.HTML(poi["storeHours"])
        store_url = "https://www.bouclair.com/en/stores/location?sid={}".format(
            poi["ID"]
        )
        location_name = poi["name"]
        street_address = poi["address1"]
        if poi["address2"]:
            street_address += " " + poi["address2"]
        street_address = street_address.strip()
        city = poi["city"]
        state = poi["stateCode"]
        zip_code = poi["postalCode"]
        country_code = poi["countryCode"]
        store_number = poi["ID"]
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["latitude"]
        longitude = poi["longitude"]
        hoo = poi_html.xpath("//text()")
        hours_of_operation = "".join(hoo) if hoo else "<MISSING>"

        item = [
            domain,
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
