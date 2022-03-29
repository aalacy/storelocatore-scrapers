import csv
import json
from lxml import etree
from sgzip.dynamic import SearchableCountries, DynamicZipAndGeoSearch

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
    session = SgRequests().requests_retry_session(retries=3, backoff_factor=0.3)

    items = []
    scraped_items = []

    DOMAIN = "alphagraphics.com"
    start_url = "https://www.alphagraphics.com/agmapapi/AGLocationFinder/SearchByLocation?ParentSiteIds%5B%5D=759afee9-1554-4283-aa6c-b1e5c4a2b1de&MetroAreaName=&SearchLocation={}&Latitude={}&Longitude={}&Radius=500"

    all_locations = []
    all_coords = DynamicZipAndGeoSearch(
        country_codes=[SearchableCountries.USA], max_search_distance_miles=500
    )
    for code, coord in all_coords:
        lat, lng = coord
        response = session.get(start_url.format(code, lat, lng))
        data = json.loads(response.text)
        if data.get("results"):
            all_locations += data["results"]

    for poi in all_locations:
        store_url = poi["url"]
        location_name = poi["title"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["addressLine1"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["city"]
        city = city if city else "<MISSING>"
        state = poi["state"]
        state = state if state else "<MISSING>"
        zip_code = poi["zip"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = poi["extCode"]
        phone = poi["fullAddress"].split("|")[-1]
        location_type = "<MISSING>"
        latitude = poi.get("lat")
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi.get("long")
        longitude = longitude if longitude else "<MISSING>"

        check = "{} {}".format(location_name, street_address)
        if check in scraped_items:
            continue
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        hoo = loc_dom.xpath('//div[@class="location-content--time"]//text()')
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
        if check not in scraped_items:
            scraped_items.append(check)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
