import csv
import json
from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w") as output_file:
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
    gathered_items = []

    DOMAIN = "monro.com"
    start_url = "https://www.monro.com/wp-json/monro/v1/stores/brand?brand=1"
    response = session.get(start_url)
    data = json.loads(response.text)

    for poi in data["data"]:
        store_url = "<MISSING>"
        location_name = poi["BrandDisplayName"]
        street_address = poi["Address"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["City"]
        city = city if city else "<MISSING>"
        state = poi["StateCode"]
        state = state if state else "<MISSING>"
        zip_code = poi["ZipCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = poi["Id"]
        phone = poi["SalesPhone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["Latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["Longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = []
        hoo_dict = {}
        for key, value in poi.items():
            if "OpenTime" in key:
                day = key.replace("OpenTime", "")
                opens = value
                if hoo_dict.get(day):
                    hoo_dict[day]["opens"] = opens
                else:
                    hoo_dict[day] = {}
                    hoo_dict[day]["opens"] = opens
            if "CloseTime" in key:
                day = key.replace("CloseTime", "")
                closes = value
                if hoo_dict.get(day):
                    hoo_dict[day]["closes"] = closes
                else:
                    hoo_dict[day] = {}
                    hoo_dict[day]["closes"] = closes

        for day, hours in hoo_dict.items():
            opens = hours["opens"]
            closes = hours["closes"]
            hours_of_operation.append(f"{day} {opens} - {closes}")
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

        check = location_name.strip().lower() + " " + street_address.strip().lower()
        if check not in gathered_items:
            gathered_items.append(check)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
