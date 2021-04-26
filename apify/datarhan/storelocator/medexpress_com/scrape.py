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
    scraped_items = []

    DOMAIN = "medexpress.com"
    start_url = "https://liveapi.yext.com/v2/accounts/me/answers/vertical/query?v=20190101&api_key=14fecb38353352245a3e1b13ed8948c0&jsLibVersion=v1.5.6&sessionTrackingEnabled=true&input=Centers%20near%20me&experienceKey=medexpressanswerstemplate&version=PRODUCTION&filters=%7B%7D&facetFilters=%7B%22c_servicesOfferedFilter%22%3A%5B%5D%7D&verticalKey=Facilities&limit=20&offset=0&queryId=78ed8f11-90a7-47ac-a88b-c7381e0c8374&retrieveFacets=true&locale=en&referrerPageUrl=https%3A%2F%2Fwww.medexpress.com%2F"

    all_poi = []
    response = session.get(start_url)
    data = json.loads(response.text)
    all_poi += data["response"]["results"]
    total_poi = data["response"]["resultsCount"] + 20
    for offset in range(20, total_poi):
        page_response = session.get(
            add_or_replace_parameter(start_url, "offset", str(offset))
        )
        page_data = json.loads(page_response.text)
        all_poi += page_data["response"]["results"]

    for poi in all_poi:
        store_url = poi["data"]["websiteUrl"]["displayUrl"]
        store_url = store_url if store_url else "<MISSING>"
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
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["data"]["id"]
        store_number = store_number if store_number else "<MISSING>"
        phone = poi["data"]["mainPhone"]
        phone = phone if phone else "<MISSING>"
        location_type = poi["data"]["type"]
        location_type = location_type if location_type else "<MISSING>"
        latitude = poi["data"]["yextDisplayCoordinate"]["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["data"]["yextDisplayCoordinate"]["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = []
        for day, hours in poi["data"]["hours"].items():
            if day == "holidayHours":
                continue
            if hours.get("openIntervals"):
                opens = hours["openIntervals"][0]["start"]
                closes = hours["openIntervals"][0]["end"]
                hours_of_operation.append("{} {} - {}".format(day, opens, closes))
            else:
                hours_of_operation.append("{} closed".format(day))
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
