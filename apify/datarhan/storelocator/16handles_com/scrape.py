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
    session = SgRequests()

    items = []

    DOMAIN = "16handles.com"
    start_url = "https://liveapi.yext.com/v2/accounts/me/answers/vertical/query"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
    }
    params = {
        "v": "20190101",
        "api_key": "ced4d8e1cfeba3cec6f6889a1fd26886",
        "jsLibVersion": "v1.6.3",
        "sessionTrackingEnabled": "true",
        "input": "stores",
        "experienceKey": "16handles",
        "version": "PRODUCTION",
        "filters": {},
        "facetFilters": {},
        "verticalKey": "locations",
        "limit": "40",
        "offset": "0",
        "retrieveFacets": "true",
        "locale": "en",
        "referrerPageUrl": "https://16handles.com/",
    }
    response = session.get(start_url, headers=headers, params=params)
    data = json.loads(response.text)

    for poi in data["response"]["results"]:
        store_url = poi["data"]["website"]
        store_url = store_url if store_url else "<MISSING>"
        location_name = poi["data"]["c_locationNickname"]
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
        store_number = "<MISSING>"
        phone = poi["data"].get("localPhone")
        if not phone:
            phone = poi["data"].get("mainPhone")
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["data"]["geocodedCoordinate"]["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["data"]["geocodedCoordinate"]["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = []
        for day, hours in poi["data"]["hours"].items():
            if type(hours) not in [str, list]:
                if hours.get("isClosed"):
                    hours_of_operation.append(f"{day} closed")
                else:
                    opens = hours["openIntervals"][0]["start"]
                    closes = hours["openIntervals"][0]["end"]
                    hours_of_operation.append(f"{day} {opens} - {closes}")
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
