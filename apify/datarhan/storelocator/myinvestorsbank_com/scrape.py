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
    session = SgRequests()

    items = []

    DOMAIN = "myinvestorsbank.com"
    start_url = "https://www.myinvestorsbank.com/OfficeSearch/OfficeSearch/GetBranches/"

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,pt;q=0.6",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
    }
    formdata = '{"Radius":100,"StartLocation":"Short Hills, NJ","Type":"Office","NodeAliasPath":"/Branch-Locations","Latitude":40.7483499,"Longitude":-74.3232194}'
    headers = {"Content-Type": "application/json"}
    response = session.post(start_url, data=formdata, headers=headers)
    data = json.loads(response.text)

    for poi in data["offices"]:
        store_url = poi["NodeAliasPath"]
        store_url = urljoin(start_url, store_url) if store_url else "<MISSING>"
        location_name = poi["Name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["Address1"]
        if poi["Address2"]:
            street_address += ", " + poi["Address2"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["City"]
        city = city if city else "<MISSING>"
        state = poi["State"]
        state = state if state else "<MISSING>"
        zip_code = poi["ZIP"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["Country"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["BranchId"]
        store_number = store_number if store_number else "<MISSING>"
        phone = poi["Phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
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

        items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
