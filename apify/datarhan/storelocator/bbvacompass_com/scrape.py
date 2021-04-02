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

    DOMAIN = "bbvausa.com"

    start_url = "https://liveapi.yext.com/v2/accounts/me/answers/vertical/query?v=20190101&api_key=7d3f010c5d39e1427b1ef79803fb493e&jsLibVersion=v1.7.2&sessionTrackingEnabled=true&input=bbva%20near%20me&experienceKey=bbvaconfig&version=PRODUCTION&filters=%7B%22c_bBVAType%22%3A%7B%22%24eq%22%3A%22BBVA%20Branch%22%7D%7D&facetFilters=%7B%7D&verticalKey=locations&limit=20&offset=20&queryId=f37ed31f-3bfc-48c6-8f6c-adeecca8e95e&locale=en&referrerPageUrl=&source=STANDARD"

    response = session.get(start_url)
    data = json.loads(response.text)
    all_locations = data["response"]["results"]
    for offset in range(20, data["response"]["resultsCount"] + 20, 20):
        response = session.get(
            add_or_replace_parameter(start_url, "offset", str(offset))
        )
        data = json.loads(response.text)
        all_locations += data["response"]["results"]

    for poi in all_locations:
        location_name = poi["data"].get("c_bBVAName")
        if not location_name:
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
        phone = poi["data"]["mainPhone"]
        phone = phone if phone else "<MISSING>"
        location_type = poi["data"]["c_bBVAType"][0]
        location_type = location_type if location_type else "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        if poi["data"].get("cityCoordinate"):
            latitude = poi["data"]["cityCoordinate"]["latitude"]
            longitude = poi["data"]["cityCoordinate"]["longitude"]
        elif poi["data"].get("displayCoordinate"):
            latitude = poi["data"]["displayCoordinate"]["latitude"]
            longitude = poi["data"]["displayCoordinate"]["longitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = []
        if poi["data"].get("hours"):
            for day, hours in poi["data"]["hours"].items():
                if type(hours) == str:
                    continue
                if day == "holidayHours":
                    continue
                if hours.get("openIntervals"):
                    hours_of_operation.append(
                        "{} {} - {}".format(
                            day,
                            hours["openIntervals"][0]["start"],
                            hours["openIntervals"][0]["end"],
                        )
                    )
                if hours.get("isClosed"):
                    hours_of_operation.append("{} - closed".format(day))
        hours_of_operation = (
            ", ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
        )

        store_url = poi["data"].get("url")
        if not store_url:
            store_url = "https://www.bbvausa.com/USA/{}/{}/{}/".format(
                state, city, street_address
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

        if location_name not in scraped_items:
            scraped_items.append(location_name)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
