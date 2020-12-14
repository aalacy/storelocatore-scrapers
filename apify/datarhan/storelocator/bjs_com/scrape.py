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

    DOMAIN = "bjs.com"
    start_url = "https://api.bjs.com/digital/live/api/v1.2/club/search/10201"
    headers = {
        "content-type": "application/json",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    }
    body = '{"Town":"","latitude":"40.75368539999999","longitude":"-73.9991637","radius":"50000","zipCode":""}'
    response = session.post(start_url, data=body, headers=headers)
    data = json.loads(response.text)

    for poi in data["Stores"]["PhysicalStore"]:
        store_url = "<MISSING>"
        location_name = poi["Description"][0]["displayStoreName"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["addressLine"][0]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["city"]
        city = city if city else "<MISSING>"
        state = poi["stateOrProvinceName"]
        state = state if state else "<MISSING>"
        zip_code = poi["postalCode"]
        zip_code = zip_code.strip() if zip_code else "<MISSING>"
        country_code = poi["country"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["storeName"]
        phone = poi.get("telephone1")
        phone = phone.strip() if phone else "<MISSING>"
        location_type = [
            elem["value"] for elem in poi["Attribute"] if elem["name"] == "StoreType"
        ]
        if location_type[0] != "CLUB":
            continue
        location_type = location_type[0] if location_type else "<MISSING>"
        latitude = poi["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = [
            elem["value"]
            for elem in poi["Attribute"]
            if elem["name"] == "Hours of Operation"
        ]
        hours_of_operation = hours_of_operation[0].replace("<br>", " ")
        hours_of_operation = (
            hours_of_operation if hours_of_operation.strip() else "<MISSING>"
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
