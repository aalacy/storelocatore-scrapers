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

    DOMAIN = "goinpostal.com"

    start_url = "https://api.goinpostal.com/stores/nearest?longitude=0&latitude=0&distance=100000"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }

    response = session.get(start_url, headers=headers)
    data = json.loads(response.text)

    for poi in data:
        store_url = (
            "https://goinpostal.com/locations/locator_store.php/?storeID={}".format(
                poi["storeIdOld"]
            )
        )
        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["address"]
        location_type = "<MISSING>"
        if "Coming Soon" in street_address:
            continue
        street_address = (
            street_address.replace("Coming Soon", "") if street_address else "<MISSING>"
        )
        street_address = (
            street_address.strip() if street_address.strip() else "<MISSING>"
        )
        city = poi["city"]
        city = city if city else "<MISSING>"
        state = poi["state"]
        state = state.replace(".", "") if state else "<MISSING>"
        zip_code = poi["zip"]
        zip_code = zip_code.strip() if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = poi["storeIdOld"]
        store_number = store_number if store_number else "<MISSING>"
        phone = poi["phone"]
        if "Coming Soon" in phone:
            phone = "<MISSING>"
        phone = phone if phone else "<MISSING>"
        latitude = poi["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["longitude"]
        longitude = longitude if longitude else "<MISSING>"

        mon = "Monday {} - {}".format(poi["fromMon"], poi["toMon"]).strip()
        tue = "Tuesday {} - {}".format(poi["fromTue"], poi["toTue"]).strip()
        wen = "Wednesday {} - {}".format(poi["fromWed"], poi["toWed"]).strip()
        thu = "Thursday {} - {}".format(poi["fromThu"], poi["toThu"]).strip()
        fri = "Friday {} - {}".format(poi["fromFri"], poi["toFri"]).strip()
        sat = "Saturday {} - {}".format(poi["fromSat"], poi["toSat"]).strip()
        sun = "Sunday {}".format(poi["fromSun"]).strip()
        hours_of_operation = [mon, tue, wen, thu, fri, sat, sun]
        hours_of_operation = (
            ", ".join(hours_of_operation).replace("None", "closed")
            if hours_of_operation
            else "<MISSING>"
        )

        if "Coming Soon" in hours_of_operation:
            continue
        if "Monday  -, Tuesday  -, Wednesday  -" in hours_of_operation:
            continue
        if hours_of_operation.endswith("Sunday"):
            hours_of_operation = hours_of_operation + " closed"
        hours_of_operation = hours_of_operation.replace(
            "Saturday  -,", "Saturday closed,"
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
