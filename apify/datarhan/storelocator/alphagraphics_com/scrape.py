import csv
import json
from lxml import etree
from sgzip.dynamic import DynamicZipSearch, SearchableCountries

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
    start_url = "https://printing-services-near-me.alphagraphics.com/search.html?q={}"

    all_locations = []
    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_radius_miles=200,
        max_search_results=None,
    )
    for code in all_codes:
        response = session.get(start_url.format(code))
        dom = etree.HTML(response.text)
        all_locations += dom.xpath(
            '//ol[@class="ResultList"]//a[@data-ya-track="website_cta"]/@href'
        )

    for store_url in list(set(all_locations)):
        if not store_url.strip():
            continue
        if "html" in store_url:
            store_url = (
                "/".join(store_url.split("/")[:-1])
                + "/"
                + store_url.split("/")[-1].replace(".", "").replace("html", ".html")
            )
        if "www.alphagraphics.com" not in store_url:
            continue
        store_response = session.get(store_url)
        store_dom = etree.HTML(store_response.text)
        poi_data = store_dom.xpath('//script[@type="application/ld+json"]/text()')
        poi_data = json.loads(poi_data[0])
        if type(poi_data) != list:
            continue

        location_name = poi_data[0].get("name")
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi_data[0]["address"]["streetAddress"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi_data[0]["address"]["addressLocality"]
        city = city if city else "<MISSING>"
        state = poi_data[0]["address"]["addressRegion"]
        state = state if state else "<MISSING>"
        zip_code = poi_data[0]["address"]["postalCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi_data[0]["address"]["addressCountry"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = "<MISSING>"
        store_number = store_number if store_number else "<MISSING>"
        phone = poi_data[0]["telephone"]
        phone = phone if phone else "<MISSING>"
        location_type = poi_data[0]["@type"]
        location_type = location_type if location_type else "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        if poi_data[0].get("hasMap"):
            latitude = poi_data[0]["hasMap"].split("/")[-1].split(",")[0]
            longitude = poi_data[0]["hasMap"].split("/")[-1].split(",")[-1]
        hours_of_operation = "<MISSING>"
        if poi_data[0].get("openingHours"):
            hours_of_operation = poi_data[0]["openingHours"]

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
        check = "{} {}".format(location_name, street_address)
        if check not in scraped_items:
            scraped_items.append(check)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
