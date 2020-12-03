import csv
import json
from sgrequests import SgRequests

DOMAIN = "moneymart.com"


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

    DOMAIN = "mrhandyman.com"
    start_url = (
        "https://www.mrhandyman.com/local-handyman-service/?CallAjax=GetLocations"
    )

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }
    response = session.post(start_url, headers=headers)
    data = json.loads(response.text)

    for poi in data:
        store_url = poi["Path"]
        store_url = "https://www.mrhandyman.com" + store_url if store_url else ""
        if not store_url:
            store_url = poi["ExternalDomain"]
        store_url = store_url if store_url else "<MISSING>"
        location_name = poi["BusinessName"]
        street_address = poi["Address1"]
        if poi["Address2"]:
            street_address += ", " + poi["Address2"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["City"]
        city = city if city else "<MISSING>"
        state = poi["State"]
        state = state if state else "<MISSING>"
        zip_code = poi["ZipCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["Country"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["FranchiseLocationID"]
        phone = poi["Phone"]
        phone = phone if phone else "<MISSING>"
        location_type = poi["LocationType"]
        location_type = location_type if location_type else "<MISSING>"
        latitude = poi["Latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["Longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = "<MISSING>"

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
