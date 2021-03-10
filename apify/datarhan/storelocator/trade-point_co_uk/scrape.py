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

    DOMAIN = "trade-point.co.uk"
    start_url = "https://api.kingfisher.com/v1/mobile/stores/TPUK?nearLatLong=51.507320%2C-0.127647&page[size]=500"
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Authorization": "Atmosphere atmosphere_app_id=kingfisher-LTbGHXKinHaJSV86nEjf0KnO70UOVE6UcYAswLuC",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
    }

    response = session.get(start_url, headers=headers)
    data = json.loads(response.text)

    for poi in data["data"]:
        store_url = "https://www.trade-point.co.uk" + poi["attributes"]["seoPath"]
        location_name = poi["attributes"]["store"]["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["attributes"]["store"]["geoCoordinates"]["address"][
            "lines"
        ][0]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["attributes"]["store"]["geoCoordinates"]["address"]["lines"][-2]
        city = city if city else "<MISSING>"
        state = poi["attributes"]["store"]["geoCoordinates"]["address"]["lines"][-1]
        state = state if state else "<MISSING>"
        zip_code = poi["attributes"]["store"]["geoCoordinates"]["postalCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["attributes"]["store"]["geoCoordinates"]["countryCode"]
        country_code = country_code.split("-")[0] if country_code else "<MISSING>"
        store_number = poi["id"]
        phone = poi["attributes"]["store"]["contactPoint"]["telephone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["attributes"]["store"]["geoCoordinates"]["coordinates"][
            "latitude"
        ]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["attributes"]["store"]["geoCoordinates"]["coordinates"][
            "longitude"
        ]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = []
        for elem in poi["attributes"]["store"]["openingHoursSpecifications"]:
            if elem.get("opens"):
                opens = ":".join(elem["opens"].split(":")[:2])
                closes = ":".join(elem["closes"].split(":")[:2])
                hours_of_operation.append(f'{elem["dayOfWeek"]} {opens} - {closes}')
            else:
                hours_of_operation.append(f'{elem["dayOfWeek"]} closed')
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
