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

    DOMAIN = "bankozarks.com"
    start_url = "https://api.ozk.com/webfunctions/GetBranches"

    response = session.get(start_url)
    data = json.loads(response.text)

    for poi in data:
        store_url = "<MISSING>"
        location_name = poi["branchName"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["address"]["street"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["address"]["city"]
        city = city if city else "<MISSING>"
        state = poi["address"]["state"]
        state = state if state else "<MISSING>"
        zip_code = poi["address"]["postalCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["address"]["country"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["costCenter"]
        store_number = store_number if store_number else "<MISSING>"
        phone = poi["primaryPhone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = []
        for day, hours in poi["hours"].items():
            if hours:
                if hours.get("blocks"):
                    opens = hours["blocks"][0]["from"]
                    opens = "{}:{}".format(opens[:-2], opens[-2:])
                    closes = hours["blocks"][0]["to"]
                    closes = "{}:{}".format(closes[:-2], closes[-2:])
                    hours_of_operation.append("{} {} - {}".format(day, opens, closes))
                else:
                    hours_of_operation.append("{} closed".format(day))
        hours_of_operation = (
            ", ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
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
