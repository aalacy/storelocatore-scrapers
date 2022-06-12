import re
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
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []

    start_url = "https://www.carolinabank.net/_/api/atms/34.1975328/-79.7679955/500"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")

    data = session.get(start_url).json()
    all_locations = data["atms"]
    for poi in all_locations:
        store_url = "https://www.carolinabank.net/about/locations"
        location_name = poi["name"]
        street_address = poi["address"]
        city = poi["city"]
        state = poi["state"]
        zip_code = poi["zip"]
        country_code = "<MISSING>"
        store_number = poi["id"]
        phone = "<MISSING>"
        location_type = "atm"
        latitude = poi["lat"]
        longitude = poi["long"]
        hours_of_operation = "<MISSING>"

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
