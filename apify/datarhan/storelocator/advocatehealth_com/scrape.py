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

    DOMAIN = "advocatehealth.com"
    start_url = "https://locator-api.localsearchprofiles.com/api/LocationSearchResults/?configuration=0462a6a3-e4be-4522-8c9c-cd008870844c&&address=40.75368539999999%2C-73.9991637&searchby=address&start=0"

    response = session.get(start_url)
    data = json.loads(response.text)
    all_poi = data["Hit"]
    total_items = data["Found"]
    for i in range(10, total_items + 10, 10):
        page_response = session.get(
            add_or_replace_parameter(start_url, "start", str(i))
        )
        page_data = json.loads(page_response.text)
        all_poi += page_data["Hit"]

    for poi in all_poi:
        store_url = poi["Fields"].get("Url")
        store_url = store_url[0] if store_url else "<MISSING>"
        location_name = poi["Fields"]["LocationName"]
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = poi["Fields"]["Address1"]
        street_address = street_address[0] if street_address else "<MISSING>"
        if poi["Fields"].get("Address2"):
            street_address += ", " + poi["Fields"]["Address2"][0]
        city = poi["Fields"]["City"]
        city = city[0] if city else "<MISSING>"
        state = poi["Fields"]["State"]
        state = state[0] if state else "<MISSING>"
        zip_code = poi["Fields"]["Zip"]
        zip_code = zip_code[0] if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = poi["Fields"]["LocationId"]
        store_number = store_number[0] if store_number else "<MISSING>"
        phone = poi["Fields"]["Phone"]
        phone = phone[0] if phone else "<MISSING>"
        location_type = poi["Fields"].get("Type")
        location_type = location_type[0] if location_type else "<MISSING>"
        latitude = poi["Fields"]["Latlng"][0].split(",")[0]
        longitude = poi["Fields"]["Latlng"][0].split(",")[-1]
        hours_of_operation = []
        if poi.get("HoursOfOperation"):
            for day, hours in poi["HoursOfOperation"].items():
                if day == "TimeZone":
                    continue
                if not hours["Hours"][0].get("OpenTime"):
                    hours_of_operation.append(f"{day} Closed")
                else:
                    opens = hours["Hours"][0]["OpenTime"]
                    closes = hours["Hours"][0]["CloseTime"]
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
