import re
import csv
import json

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
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []

    start_url = "https://afsshareportal.com/lookUpFeatures.php?callback=jsonpcallbackInfo&action=storeInfo&website_url=leesmarketplace.com"
    domain = "leesmarketplace.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    data = re.findall(r"jsonpcallbackInfo\((.+)\)", response.text)[0]

    all_locations = json.loads(data)
    for poi in all_locations:
        store_url = "https://leesmarketplace.com/" + poi["store_city"].lower()
        location_name = poi["store_name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["store_address"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["store_city"]
        city = city if city else "<MISSING>"
        state = poi["store_state"]
        state = state if state else "<MISSING>"
        zip_code = poi["store_zip"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = poi["store_id"]
        phone = poi["store_phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["store_lat"]
        longitude = poi["store_lng"]
        hoo_1 = f'Mon-Sat: {poi["store_hMonOpen"]} - {poi["store_hSatClose"]}'
        hoo_2 = f'Sunday: {poi["store_hSunOpen"]} - {poi["store_hSunClose"]}'
        hours_of_operation = f"{hoo_1} {hoo_2}"

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

        items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
