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

    DOMAIN = "webuy.com"
    start_url = "https://wss2.cex.uk.webuy.io/v3/stores"

    response = session.get(start_url)
    data = json.loads(response.text)

    for poi in data["response"]["data"]["stores"]:
        store_url = "https://wss2.cex.uk.webuy.io/v3/stores/{}/detail".format(
            poi["storeId"]
        )
        loc_response = session.get(store_url)
        data = json.loads(loc_response.text)
        data = data["response"]["data"]["store"]

        location_name = poi["storeName"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = data["addressLine1"]
        if data["addressLine2"]:
            street_address += ", " + data["addressLine2"]
        street_address = street_address if street_address else "<MISSING>"
        city = data["city"]
        city = city if city else "<MISSING>"
        state = data["county"]
        state = state if state else "<MISSING>"
        zip_code = data["postcode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = data["country"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["storeId"]
        store_number = store_number if store_number else "<MISSING>"
        phone = "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = []
        for day in data["timings"]["open"].keys():
            hours_of_operation.append(
                f"{day} {data['timings']['open'][day]} - {data['timings']['close'][day]}"
            )
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
