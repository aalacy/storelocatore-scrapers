import csv
import json
from urllib.parse import urljoin

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

    DOMAIN = "hollandandbarrett.com"
    start_url = "https://api.woosmap.com/stores/search"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0",
        "Accept": "*/*",
        "Accept-Language": "uk-UA,uk;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://www.hollandandbarrett.com/stores/",
        "Origin": "https://www.hollandandbarrett.com",
        "Connection": "keep-alive",
        "TE": "Trailers",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }

    params = (
        ("key", "woos-7dcebde8-9cf4-37a7-bac3-1dce1c0942ee"),
        ("lat", "51.50732"),
        ("lng", "-0.12764746"),
        ("max_distance", "50000"),
        ("stores_by_page", "250"),
        ("limit", "1000"),
        ("page", "1"),
    )

    response = session.get(start_url, headers=headers, params=params)
    data = json.loads(response.text)

    for poi in data["features"]:
        base_url = "https://www.hollandandbarrett.com"
        store_url = urljoin(base_url, poi["properties"]["user_properties"]["storePath"])
        location_name = poi["properties"]["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = " ".join(poi["properties"]["address"]["lines"]).lower()
        city = poi["properties"]["address"]["city"]
        if street_address.endswith(city.lower()):
            street_address = " ".join(street_address.split(city.lower())[:-1])
        street_address = street_address.upper()
        state = "<MISSING>"
        zip_code = poi["properties"]["address"]["zipcode"]
        country_code = poi["properties"]["address"]["country_code"]
        store_number = poi["properties"]["store_id"]
        phone = poi["properties"]["contact"]["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = poi["properties"]["types"][0]
        latitude = poi["geometry"]["coordinates"][1]
        longitude = poi["geometry"]["coordinates"][0]
        days_dict = {
            "1": "Monday",
            "2": "Tuesday",
            "3": "Wendsday",
            "4": "Thursday",
            "5": "Friday",
            "6": "Satarday",
            "7": "Sunday",
        }
        hours_of_operation = []
        for key, hours in poi["properties"]["opening_hours"]["usual"].items():
            day = days_dict[key]
            if hours:
                opens = hours[0]["start"]
                closes = hours[0]["end"]
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
