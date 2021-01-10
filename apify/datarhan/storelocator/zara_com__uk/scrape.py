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
    items = []

    session = SgRequests()

    DOMAIN = "zara.com"

    cities = [
        ("51.5073509", "-0.1277583"),
        ("53.4083714", "-2.9915726"),
        ("51.48158100000001", "-3.17909"),
        ("50.90970040000001", "-1.4043509"),
        ("50.82253000000001", "-0.137163"),
        ("51.7520209", "-1.2577263"),
        ("52.205337", "0.121817"),
    ]
    all_locations = []
    for lat, lng in cities:
        url = "https://www.zara.com/uk/en/stores-locator/search?lat={}&lng={}&isGlobalSearch=true&showOnlyPickup=false&isDonationOnly=false&ajax=true"
        response = session.get(url.format(lat, lng))
        data = json.loads(response.text)
        all_locations += data

    for poi in all_locations:
        store_url = "<MISSING>"
        location_name = poi["addressLines"][0]
        street_address = poi["addressLines"][0]
        city = poi["city"]
        city = city if city else "<MISSING>"
        state = poi["state"]
        zip_code = poi["zipCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["countryCode"]
        store_number = poi["id"]
        phone = poi["phones"]
        phone = phone[0] if phone else "<MISSING>"
        location_type = poi["datatype"]
        latitude = poi["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["longitude"]
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
