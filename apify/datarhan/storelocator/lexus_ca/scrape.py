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

    DOMAIN = "lexus.ca"
    start_url = "https://www.lexus.ca/lexus/src/data/dealer/.json"
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36"
    }
    response = session.get(start_url, headers=headers)
    data = json.loads(response.text)

    for loc_id, poi in data["dealers"].items():
        store_url = f"https://www.lexus.ca/lexus/en/dealership/{loc_id}"
        location_name = poi["name"]["en"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["address"]["streetAddress"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["address"]["city"]
        state = poi["address"]["province"]
        zip_code = poi["address"]["postalCode"]
        country_code = "<MISSING>"
        store_number = poi["associationId"]
        phone = poi["phoneNumbers"][0]["CompleteNumber"]["$"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["location"]["lat"]
        longitude = poi["location"]["lng"]
        hours_of_operation = []
        hoo = [
            elem
            for elem in poi["departments"]
            if elem["name"]["en"] == "New Vehicle Sales"
        ][0]
        if hoo.get("hours"):
            hoo = hoo["hours"]
            for elem in hoo:
                if elem.get("toDay"):
                    hours_of_operation.append(
                        f'{elem["fromDay"]["en"]} - {elem["toDay"]["en"]} {elem["startTime"]["en"]} - {elem["endTime"]["en"]}'
                    )
                else:
                    hours_of_operation.append(
                        f'{elem["fromDay"]["en"]} {elem["startTime"]["en"]} - {elem["endTime"]["en"]}'
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
