import re
import csv
import json
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
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

    DOMAIN = "regions.com"

    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_radius_miles=30,
        max_search_results=None,
    )

    start_url = "https://www.regions.com/Locator?regions-get-directions-starting-coords=&daddr=&autocompleteAddLat=&autocompleteAddLng=&r=&geoLocation={}&type=branch"

    for code in all_codes:
        response = session.get(start_url.format(code))
        dom = etree.HTML(response.text)

        all_poi = dom.xpath('//script[contains(text(), "searchResults")]/text()')[0]
        all_poi = re.findall(
            "searchResults =(.+);", all_poi.replace("\r", "").replace("\n", "")
        )[0]
        all_poi = json.loads(all_poi.replace("/* forcing open state for all FCs*/", ""))
        for poi in all_poi:
            if type(poi) == str:
                continue
            store_url = "<MISSING>"
            location_name = poi["title"]
            location_name = location_name if location_name else "<MISSING>"
            street_address = poi["address"].split("<br />")[0]
            street_address = street_address if street_address else "<MISSING>"
            city = poi["address"].split("<br />")[-1].split(",")[0]
            city = city if city else "<MISSING>"
            state = poi["address"].split("<br />")[-1].split(",")[-1].split()[0]
            state = state if state else "<MISSING>"
            zip_code = poi["address"].split("<br />")[-1].split(",")[-1].split()[-1]
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = poi["geolocation"]
            country_code = country_code if country_code else "<MISSING>"
            store_number = ""
            store_number = store_number if store_number else "<MISSING>"
            phone = ""
            phone = phone if phone else "<MISSING>"
            location_type = poi["type"]
            location_type = location_type if location_type else "<MISSING>"
            latitude = poi["lat"]
            latitude = latitude if latitude else "<MISSING>"
            longitude = poi["lng"]
            longitude = longitude if longitude else "<MISSING>"
            hours_of_operation = poi["hours"]
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

            if location_name not in scraped_items:
                scraped_items.append(location_name)
                items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
