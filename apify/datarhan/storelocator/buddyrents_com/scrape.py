import csv
import json

from sgrequests import SgRequests
from sgzip.dynamic import DynamicZipSearch, SearchableCountries


def write_output(data):
    with open("data.csv", mode="w") as output_file:
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

    DOMAIN = "buddyrents.com"
    start_url = "https://www.buddyrents.com/store/storelocator/search"

    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_radius_miles=50,
        max_search_results=None,
    )

    all_locations = []
    for code in all_codes:
        formdata = {"zipcode": code}
        response = session.post(start_url, data=formdata)
        data = json.loads(response.text)
        if type(data) == list:
            all_locations += data

    for poi in all_locations:
        store_url = poi["store_page_url"]
        location_name = poi["store"].split(":")[0]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["store"].split(":")[-1].split(" - ")[0].strip()
        city = poi["store"].split(":")[-1].split(" - ")[-1].split(", ")[0].strip()
        state = poi["store"].split(":")[-1].split(" - ")[-1].split(", ")[-1].split()[0]
        zip_code = (
            poi["store"].split(":")[-1].split(" - ")[-1].split(", ")[-1].split()[-1]
        )
        country_code = "<MISSING>"
        store_number = ""
        if "#" in location_name:
            store_number = location_name.split("#")[-1]
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = "{} {} {}".format(
            poi["hours1"], poi["hours2"], poi["hours3"]
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
