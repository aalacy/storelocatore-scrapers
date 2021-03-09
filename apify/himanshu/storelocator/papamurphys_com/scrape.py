import re
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

    start_url = "https://order.papamurphys.com/api/vendors/regions?excludeCities=true"
    domain = "papamurphys.com"
    hdr = {
        "__requestverificationtoken": "",
        "accept": "application/json",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,pt;q=0.6",
        "referer": "https://order.papamurphys.com/?_ga=2.197090219.641204061.1615309632-2036711642.1615309632",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.192 Safari/537.36",
        "x-olo-request": "1",
        "x-olo-viewport": "Desktop",
        "x-requested-with": "XMLHttpRequest",
    }
    all_locations = []
    response = session.get(start_url, headers=hdr)
    data = json.loads(response.text)
    for elem in data:
        state = elem["code"]
        state_url = f"https://order.papamurphys.com/api/vendors/search/{state}"
        response = session.get(state_url, headers=hdr)
        data = json.loads(response.text)
        all_locations += data["vendor-search-results"]

    for poi in all_locations:
        store_url = urljoin(start_url, poi["slug"])
        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["streetAddress"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["city"]
        city = city if city else "<MISSING>"
        state = poi["state"]
        state = state if state else "<MISSING>"
        zip_code = poi["address"]["postalCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["address"]["country"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["id"]
        phone = poi["phoneNumber"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["latitude"]
        longitude = poi["longitude"]
        hoo = []
        for elem in poi["weeklySchedule"]["calendars"][0]["schedule"]:
            day = elem["weekDay"]
            hours = elem["description"]
            hoo.append(f"{day} {hours}")
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

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
