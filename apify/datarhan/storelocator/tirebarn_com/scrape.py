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

    DOMAIN = "tirebarn.com"
    start_url = "https://www.tirebarn.com/wp-json/monro/v1/stores/brand?brand=3"

    response = session.get(start_url)
    data = json.loads(response.text)

    for poi in data["data"]:
        store_url = "<MISSING>"
        location_name = poi["BrandDisplayName"]
        location_name = location_name if location_name else "<MISSING>"
        store_number = poi["Id"]
        street_address = poi["Address"]
        if poi["Address2"]:
            street_address += ", " + poi["Address2"]
        city = poi["City"]
        state = poi["StateCode"]
        zip_code = poi["ZipCode"]
        country_code = "<MISSING>"
        phone = poi["SalesPhone"]
        location_type = "<MISSING>"
        latitude = poi["Latitude"]
        longitude = poi["Longitude"]
        hoo = {}
        for key, hours in poi.items():
            if "Close" in key:
                day = key.split("Close")[0]
                if hoo.get(day):
                    hoo[day]["closes"] = ":".join(hours.split(":")[:2])
                else:
                    hoo[day] = {}
                    hoo[day]["closes"] = ":".join(hours.split(":")[:2])
            elif "Open" in key:
                day = key.split("Open")[0]
                if hoo.get(day):
                    hoo[day]["opens"] = ":".join(hours.split(":")[:2])
                else:
                    hoo[day] = {}
                    hoo[day]["opens"] = ":".join(hours.split(":")[:2])
        hours_of_operation = []
        for day, hours in hoo.items():
            opens = hours["opens"]
            closes = hours["closes"]
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
