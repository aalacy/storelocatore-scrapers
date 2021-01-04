import re
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

    DOMAIN = "mrgattispizza.com"
    start_url = "https://cdn.storelocatorwidgets.com/json/583c916beabda4913ceabbdd59df7689?callback=slw"

    response = session.get(start_url)
    data = re.findall(r"slw\((.+)\)", response.text)[0]
    data = json.loads(data)

    for poi in data["stores"]:
        store_url = poi["data"].get("website")
        store_url = store_url if store_url else "<MISSING>"
        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        address_raw = poi["data"]["address"].split(", ")
        street_address = "<MISSING>"
        city = "<MISSING>"
        state = "<MISSING>"
        zip_code = "<MISSING>"
        country_code = address_raw[-1]
        if len(address_raw) == 4:
            if "US" not in address_raw[-1]:
                address_raw = [", ".join(address_raw[:2])] + address_raw[2:] + ["US"]
            street_address = address_raw[0]
            city = address_raw[1]
            state = address_raw[2].split()[0]
            zip_code = address_raw[2].split()[-1]
            country_code = address_raw[-1]
        if len(address_raw) == 5:
            street_address = address_raw[0]
            street_address = street_address if street_address else "<MISSING>"
            city = address_raw[1]
            city = city if city else "<MISSING>"
            state = address_raw[2]
            state = state if state else "<MISSING>"
            zip_code = address_raw[3]
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = address_raw[-1]
            country_code = country_code if country_code else "<MISSING>"
        elif len(address_raw) == 3:
            street_address = address_raw[0]
            city = address_raw[1]
            state = address_raw[2].split()[0]
            zip_code = address_raw[2].split()[-1]
            country_code = "<MISSING>"
        elif len(address_raw) == 2:
            if "\r\n" in address_raw[0]:
                street_address = ", ".join(address_raw[0].split("\r\n")[:-1])
                city = address_raw[0].split("\r\n")[-1]
                state = address_raw[1].split(".")[0]
                zip_code = address_raw[1].split(".")[-1]
                country_code = "<MISSING>"
            else:
                street_address = "<MISSING>"
                city = address_raw[0]
                state = address_raw[1]
                zip_code = "<MISSING>"
                country_code = "<MISSING>"

        store_number = poi["storeid"]
        store_number = store_number if store_number else "<MISSING>"
        phone = poi["data"].get("phone")
        phone = phone if phone else "<MISSING>"
        location_type = ", ".join(poi["filters"])
        location_type = location_type if location_type else "<MISSING>"
        latitude = poi["data"]["map_lat"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["data"]["map_lng"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = []
        for day, hours in poi["data"].items():
            if "hours" in day:
                hours_of_operation.append("{} {}".format(day.split("_")[-1], hours))
        hours_of_operation = (
            " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
        )

        if "Coming Soon" in location_name:
            hours_of_operation = "Coming Soon"

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
