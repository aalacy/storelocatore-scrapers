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

    DOMAIN = "sunshinefoodstores.com"
    start_url = "https://sunshinefoodstores.com/ajax/index.php"

    formdata = {
        "method": "POST",
        "apiurl": "https://sunshinefoodstores.rsaamerica.com/Services/SSWebRestApi.svc/GetClientStores/1",
    }
    response = session.post(start_url, data=formdata)
    data = json.loads(response.text)

    for poi in data["GetClientStores"]:
        store_url = "https://sunshinefoodstores.com/contact"
        location_name = poi["ClientStoreName"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["AddressLine1"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["City"]
        city = city if city else "<MISSING>"
        state = poi["StateName"]
        state = state if state else "<MISSING>"
        zip_code = poi["ZipCode"]
        zip_code = zip_code.split()[-1] if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = poi["StoreNumber"]
        store_number = store_number if store_number else "<MISSING>"
        phone = poi["StorePhoneNumber"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["Latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["Longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = poi["StoreTimings"]
        hours_of_operation = hours_of_operation if hours_of_operation else "<MISSING>"

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
