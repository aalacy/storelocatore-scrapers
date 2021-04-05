import csv
import json
from datetime import datetime, timezone
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

    DOMAIN = "spacesworks.com"
    start_url = "https://api.spacesworks.com/ws/rest/marketing/v1/locations?itemsPerPage=100&pageIndex=1&locale=en_GB"

    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,pt;q=0.6",
        "authorization": "Basic c3BhY2Vzd29ya3NAc3BhY2VzYnYtSzdUTVJIOmVmNmJlYWJjLTYwMTctNGYzMC04NDlhLTQ1YjY0N2I1NWVkMg==",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.192 Safari/537.36",
        "x-ga-clientid": "1722608705.1614690743",
        "x-geo-iso2": "US",
    }
    response = session.get(start_url, headers=headers)
    data = json.loads(response.text)
    all_locations = data["data"]["items"]
    total_pages = data["data"]["totalItems"] // 100 + 2
    for page in range(2, total_pages):
        response = session.get(
            add_or_replace_parameter(start_url, "pageIndex", str(page)), headers=headers
        )
        data = json.loads(response.text)
        all_locations += data["data"]["items"]

    for poi in all_locations:
        country_code = poi["countryId"]
        if country_code not in ["US", "CA", "GB"]:
            continue
        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["addressLine1"]
        if poi.get("addressLine2"):
            street_address += " " + poi["addressLine2"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["city"]
        state = poi.get("state")
        state = state if state else "<MISSING>"
        zip_code = poi["postalCode"]
        country_code = poi["countryId"]
        store_number = poi["id"]
        phone = poi.get("phone")
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        time = str(poi["openingDate"])
        if datetime.fromisoformat(time) > datetime.now(timezone.utc):
            location_type = "coming soon"
        latitude = poi["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hoo = []
        days_dict = {
            0: "Sunday",
            1: "Monday",
            2: "Tuesday",
            3: "Wednesday",
            4: "Thursday",
            5: "Friday",
            6: "Saturday",
        }
        for elem in poi["days"]:
            day = days_dict[elem["day"]]
            opens = elem["openingTime"]
            closes = elem["closingTime"]
            hoo.append(f"{day} {opens} - {closes}")
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"
        store_url = "https://www.spacesworks.com/{}/{}/".format(
            city.replace(" ", "-").lower(), location_name.lower().replace(" ", "-")
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
