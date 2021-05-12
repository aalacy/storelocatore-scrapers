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

    DOMAIN = "jollyes.co.uk"
    start_url = "https://api.jollyes.co.uk/api/ext/aureatelabs/storeList"

    response = session.get(start_url)
    data = json.loads(response.text)

    for poi in data["result"]:
        store_url = "https://www.jollyes.co.uk/store/{}".format(poi["uid"])
        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["streetAddress"]
        city = poi["city"]
        city = city if city else "<MISSING>"
        state = poi["county"]
        state = state if state else "<MISSING>"
        zip_code = poi["postCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = poi["phoneNumber"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["map"]["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["map"]["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hoo = []
        for key, value in poi.items():
            if "Opening" in key:
                day = key.replace("Opening", "")
                if value:
                    opens = value[:2] + ":" + value[2:]
                    closes = poi["{}Closing".format(day)]
                    closes = closes[:2] + ":" + closes[2:]
                    hoo.append(f"{day} {opens} - {closes}")
                else:
                    hoo.append(f"{day} closed")
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

        items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
