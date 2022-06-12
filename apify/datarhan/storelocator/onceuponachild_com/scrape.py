import csv
import json
from time import sleep
from w3lib.url import add_or_replace_parameter

from sgrequests import SgRequests
from sgselenium import SgFirefox


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
    session = SgRequests()

    items = []
    scraped_items = []

    DOMAIN = "onceuponachild.com"
    start_url = "https://www.onceuponachild.com/locations?country=US&state=AL"

    with SgFirefox() as driver:
        driver.get(start_url)
        sleep(10)
        cookies = driver.get_cookies()

    for cookie in cookies:
        if cookie["name"] == "ouac_.token":
            token = cookie["value"]

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Authorization": f"Bearer {token}",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36",
    }

    url = "https://api.ordercloud.io/v1/suppliers?page=1&pageSize=100&Active=true&xp.isCoop=false"
    data = session.get(url, headers=headers).json()
    all_locations = data["Items"]
    total_pages = data["Meta"]["TotalPages"] + 1
    for page in range(2, total_pages):
        data = session.get(
            add_or_replace_parameter(url, "page", str(page)), headers=headers
        ).json()
        all_locations += data["Items"]

    for poi in all_locations:
        store_url = "https://www.onceuponachild.com/locations/" + poi["xp"]["slug"]
        loc_response = session.get(
            f'https://api.ordercloud.io/v1/suppliers/{poi["ID"]}/addresses/{poi["ID"]}',
            headers=headers,
        )
        data = json.loads(loc_response.text)

        location_name = poi["Name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = data["Street1"]
        if data["Street2"]:
            street_address += " " + data["Street2"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["xp"]["city"]
        city = city if city else "<MISSING>"
        state = poi["xp"]["state"]
        state = state if state else "<MISSING>"
        zip_code = poi["xp"]["zip"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["xp"]["country"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["ID"]
        phone = data["Phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["xp"]["latitude"]
        longitude = poi["xp"]["longitude"]
        hoo = []
        for day, hours in data["xp"]["hours"].items():
            hoo.append(f"{day} {hours}")
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

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

        check = location_name.strip().lower() + " " + street_address.strip().lower()
        if check not in scraped_items:
            scraped_items.append(check)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
