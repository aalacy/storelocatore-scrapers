import csv
import json
from w3lib.url import add_or_replace_parameter

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

    DOMAIN = "yogurt-land.com"
    start_url = "https://www.yogurt-land.com/api/1.1/locations/search.json?include-html=1&location-selector-type=&zip-code-or-address-hidden=&page=1&lng=&lat=&favorite-location=0&search="
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36"
    }

    response = session.get(start_url, headers=headers)
    data = json.loads(response.text)
    all_locations = data["locations"]

    next_page = data["has_more"]
    while next_page:
        page_num = str(int(data["page"]) + 1)
        next_page_url = add_or_replace_parameter(start_url, "page", page_num)
        response = session.get(next_page_url, headers=headers)
        data = json.loads(response.text)
        all_locations += data["locations"]
        next_page = data["has_more"]

    for poi in all_locations:
        store_url = "https://www.yogurt-land.com/locations/view/{}/{}".format(
            poi["Location"]["id"], poi["Location"]["name"].replace(" & ", "-")
        )
        store_url = store_url if store_url else "<MISSING>"
        location_name = poi["Location"]["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["Location"]["address"]
        if poi["Location"]["address_2"]:
            street_address += ", " + poi["Location"]["address_2"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["Location"]["city"]
        city = city if city else "<MISSING>"
        state = poi["Location"]["state_code"]
        state = state if state else "<MISSING>"
        zip_code = poi["Location"]["postal_code"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["Location"]["country_code"]
        country_code = country_code if country_code else "<MISSING>"
        if country_code not in ["US", "CA"]:
            continue
        store_number = poi["Location"]["id"]
        store_number = store_number if store_number else "<MISSING>"
        phone = poi["Location"]["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        location_type = location_type if location_type else "<MISSING>"
        latitude = poi["Location"]["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["Location"]["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = poi["Location"]["formatted_hours"]
        hours_of_operation = (
            hours_of_operation.replace("<br />", " ")
            if hours_of_operation
            else "<MISSING>"
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

        items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
