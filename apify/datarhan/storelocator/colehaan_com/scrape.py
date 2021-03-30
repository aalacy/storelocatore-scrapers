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

    DOMAIN = "colehaan.com"
    start_url = "https://liveapi.yext.com/v2/accounts/me/answers/vertical/query?v=20190101&api_key=c202b999eeb9609ed15439271ae840c7&jsLibVersion=v1.4.8&sessionTrackingEnabled=true&input=Open%20locations%20near%20me&experienceKey=colehaan-answers&version=PRODUCTION&filters=%7B%7D&facetFilters=%7B%7D&verticalKey=locations&limit=40&offset=0&retrieveFacets=true&locale=en"
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36"
    }

    response = session.get(start_url, headers=headers)
    data = json.loads(response.text)
    all_locations = data["response"]["results"]
    total = data["response"]["resultsCount"]
    for index in range(40, total + 40, 40):
        response = session.get(
            add_or_replace_parameter(start_url, "offset", str(index)), headers=headers
        )
        data = json.loads(response.text)
        all_locations += data["response"]["results"]

    for poi in all_locations:
        store_url = poi["data"]["websiteUrl"]["displayUrl"]
        location_name = poi["data"]["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["data"]["address"]["line1"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["data"]["address"]["city"]
        city = city if city else "<MISSING>"
        state = poi["data"]["address"]["region"]
        state = state if state else "<MISSING>"
        zip_code = poi["data"]["address"]["postalCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["data"]["address"]["countryCode"]
        store_number = poi["data"]["id"]
        store_number = store_number if store_number else "<MISSING>"
        phone = poi["data"]["mainPhone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["data"]["geocodedCoordinate"]["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["data"]["geocodedCoordinate"]["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = []
        for day, hours in poi["data"]["hours"].items():
            if hours.get("openIntervals"):
                opens = hours["openIntervals"][0]["start"]
                closes = hours["openIntervals"][0]["end"]
                hours_of_operation.append(f"{day} {opens} - {closes}")
            else:
                hours_of_operation.append(f"{day} closed")
        hours_of_operation = (
            " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
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
