import csv
import json

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
    items = []
    scraped_items = []

    session = SgRequests()

    DOMAIN = "zara.com"

    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36",
        "content-type": "application/json",
    }
    all_locations = []
    ca_codes = DynamicGeoSearch(
        country_codes=[SearchableCountries.CANADA], max_radius_miles=100
    )
    uk_codes = DynamicGeoSearch(
        country_codes=[SearchableCountries.BRITAIN], max_radius_miles=50
    )
    us_codes = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA], max_radius_miles=100
    )
    all_countries = {"CA": ca_codes, "US": us_codes, "UK": uk_codes}
    for country_code, coordinates in all_countries.items():
        for lat, lng in coordinates:
            url = "https://www.zarahome.com/itxrest/2/bam/store/84009906/physical-store?languageId=-1&latitude={}&longitude={}&receiveEcommerce=false&countryCode{}=&min=20&max=20&appId=1"
            response = session.get(url.format(lat, lng, country_code), headers=hdr)
            data = json.loads(response.text)
            all_locations += data["closerStores"]

    for poi in all_locations:
        store_url = poi["url"]
        location_name = poi["name"]
        street_address = " ".join(poi["addressLines"])
        city = poi["city"]
        city = city if city else "<MISSING>"
        state = poi["state"]
        zip_code = poi["zipCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["countryCode"]
        if country_code not in ["GB", "CA", "US"]:
            continue
        store_number = poi["id"]
        phone = poi["phones"]
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = "<MISSING>"

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
        check = f"{location_name} {street_address}"
        if check not in scraped_items:
            scraped_items.append(check)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
