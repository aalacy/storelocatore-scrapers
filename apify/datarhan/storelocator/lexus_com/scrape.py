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

    DOMAIN = "lexus.com"
    start_url = "https://www.lexus.com/rest/lexus/dealers?experience=dealers"
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36"
    }
    response = session.get(start_url, headers=headers)
    data = json.loads(response.text)

    for poi in data["dealers"]:
        store_url = "https://www.lexus.com/dealers/{}-{}".format(
            poi["id"], poi["dealerName"].lower()
        )
        location_name = poi["dealerName"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["dealerAddress"]["address1"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["dealerAddress"]["city"]
        state = poi["dealerAddress"]["state"]
        zip_code = poi["dealerAddress"]["zipCode"]
        country_code = "<MISSING>"
        store_number = poi["id"]
        phone = poi["dealerPhone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["dealerLatitude"]
        longitude = poi["dealerLongitude"]
        hours_of_operation = []
        if poi.get("hoursOfOperation"):
            if poi["hoursOfOperation"].get("Sales"):
                for day, hours in poi["hoursOfOperation"]["Sales"].items():
                    hours_of_operation.append(f"{day} {hours}")
            else:
                for day, hours in poi["hoursOfOperation"]["Service"].items():
                    hours_of_operation.append(f"{day} {hours}")
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
