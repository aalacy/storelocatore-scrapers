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
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36"
    }
    all_locations = []
    all_coordinates = DynamicGeoSearch(
        country_codes=[SearchableCountries.BRITAIN], max_radius_miles=30
    )
    for lat, lng in all_coordinates:
        url = f"https://www.zara.com/uk/en/stores-locator/search?lat={lat}&lng={lng}&isGlobalSearch=true&showOnlyPickup=false&isDonationOnly=false&ajax=true"
        response = session.get(url, headers=hdr)
        data = json.loads(response.text)
        all_locations += data

    for poi in all_locations:
        store_url = "<MISSING>"
        location_name = poi["addressLines"][0]
        street_address = poi["addressLines"][0]
        city = poi["city"]
        city = city if city else "<MISSING>"
        state = poi["state"]
        zip_code = poi["zipCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["countryCode"]
        store_number = poi["id"]
        phone = poi["phones"]
        phone = phone[0] if phone else "<MISSING>"
        location_type = poi["datatype"]
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
        if store_number not in scraped_items:
            scraped_items.append(store_number)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
