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

    DOMAIN = "carrierenterprise.com"
    start_url = "https://www.carrierenterprise.com/storelocator/index/storeSearch/?lat=42.5629855&lng=-92.49999179999999&radius=10000"

    response = session.get(start_url)
    data = json.loads(response.text)

    for poi in data["stores"]:
        store_url = poi["branch_info_url"]
        location_name = poi["branch_name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["branch_add2"]
        if not street_address:
            street_address = poi["branch_add1"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["branch_city"]
        city = city if city else "<MISSING>"
        state = poi["branch_state"]
        state = state if state else "<MISSING>"
        zip_code = poi["branch_zip"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = ""
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["branch_id"]
        store_number = store_number if store_number else "<MISSING>"
        phone = poi["branch_phone"]
        phone = phone if phone else "<MISSING>"
        location_type = ""
        location_type = location_type if location_type else "<MISSING>"
        latitude = poi["lattitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = []
        hours_dict = {}
        for key, value in poi.items():
            if "open" in key:
                day = key.split("_")[1]
                open_hours = value
                if not open_hours:
                    open_hours = "closed"
                if hours_dict.get(day):
                    hours_dict[day]["opens"] = open_hours
                else:
                    hours_dict[day] = {}
                    hours_dict[day]["opens"] = open_hours
            if "close" in key:
                day = key.split("_")[1]
                close_hours = value
                if not close_hours:
                    close_hours = "closed"
                if hours_dict.get(day):
                    hours_dict[day]["closes"] = close_hours
                else:
                    hours_dict[day] = {}
                    hours_dict[day]["closes"] = close_hours
        for day, hours in hours_dict.items():
            hours_of_operation.append(
                "{} {} - {}".format(day, hours["opens"], hours["closes"])
            )
        hours_of_operation = (
            ", ".join(hours_of_operation).replace("closed - closed", "closed")
            if hours_of_operation
            else "<MISSING>"
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
