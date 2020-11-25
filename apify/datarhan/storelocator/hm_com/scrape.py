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

    DOMAIN = "hm.com"

    start_url = "https://api.storelocator.hmgroup.tech/v2/brand/hm/stores/locale/en_US/country/US?_type=json&campaigns=true&departments=true&openinghours=true&maxnumberofstores=1000"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36"
    }

    response = session.get(start_url, headers=hdr)
    data = json.loads(response.text)
    all_poi = data["stores"]

    ca_url = "https://api.storelocator.hmgroup.tech/v2/brand/hm/stores/locale/en_US/country/CA?_type=json&campaigns=true&departments=true&openinghours=true&maxnumberofstores=1000"
    ca_response = session.get(ca_url, headers=hdr)
    ca_data = json.loads(ca_response.text)
    all_poi += ca_data["stores"]

    for poi in all_poi:
        store_url = "<MISSING>"
        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["address"]["streetName2"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["city"]
        city = city if city else "<MISSING>"
        state = poi["region"]["name"]
        state = state if state else "<MISSING>"
        zip_code = poi["address"]["postCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["countryCode"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["storeCode"]
        store_number = store_number if store_number else "<MISSING>"
        phone = poi.get("phone")
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        location_type = location_type if location_type else "<MISSING>"
        latitude = poi["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = []
        for elem in poi["openingHours"]:
            hours_of_operation.append(
                "{} {} - {}".format(elem["name"], elem["opens"], elem["closes"])
            )
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
