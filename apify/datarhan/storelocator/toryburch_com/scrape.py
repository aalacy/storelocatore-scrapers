import csv

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
    items = []

    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    DOMAIN = "toryburch.com"
    start_url = "https://www.toryburch.com/api/prod-r2/v1/locations/offlineLocations?site=ToryBurch_US"

    headers = {
        "accept": "application/json",
        "accept-encoding": "gzip, deflate, br",
        "content-type": "application/json",
        "locale": "en_US",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
        "x-api-key": "yP6bAmceig0QmrXzGfx3IG867h5jKkAs",
    }

    data = session.get(start_url, headers=headers).json()
    all_locations = data["offlineLocations"]

    for poi in all_locations:
        store_url = "https://www.toryburch.com/store-locator/"
        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["address"]["line1"]
        if poi["address"].get("line2"):
            street_address += " " + poi["address"]["line2"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["address"]["city"]
        city = city if city else "<MISSING>"
        state = poi["address"].get("region")
        state = state if state else "<MISSING>"
        zip_code = poi["address"].get("postalCode")
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["address"]["countryCode"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["id"]
        phone = poi.get("phone")
        phone = phone if phone else "<MISSING>"
        location_type = poi.get("storeType")
        location_type = location_type if location_type else "<MISSING>"
        latitude = poi["coordinate"]["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["coordinate"]["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hoo = []
        for elem in poi["hours"]:
            day = elem["weekDay"]
            if elem.get("openIntervals"):
                opens = elem["openIntervals"][0]["start"]
                closes = elem["openIntervals"][0]["end"]
                hoo.append(f"{day} {opens} - {closes}")
            else:
                hoo.append(f"{day} closed")
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

        items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
