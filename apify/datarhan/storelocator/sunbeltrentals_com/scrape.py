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
    scraped_items = []

    DOMAIN = "sunbeltrentals.com"

    start_url = "https://www.sunbeltrentals.com/locations/getprofitcenterlist"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }

    response = session.get(start_url, headers=headers)
    data = json.loads(response.text)

    for poi in data:
        store_url = "https://www.sunbeltrentals.com/locations" + poi["Url"]
        location_name = poi["DisplayName"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["Address"]["Address1"]
        if poi["Address"]["Address2"]:
            street_address += " " + poi["Address"]["Address2"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["Address"]["City"]
        city = city if city else "<MISSING>"
        state = poi["Address"]["State"]
        state = state if state else "<MISSING>"
        zip_code = poi["Address"]["Zip"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["Address"]["Country"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["PCNumber"]
        store_number = store_number if store_number else "<MISSING>"
        phone = poi["PhoneNumber"]
        phone = phone if phone else "<MISSING>"
        location_type = ""
        location_type = location_type if location_type else "<MISSING>"
        latitude = poi["Address"]["Latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["Address"]["Longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = []
        if poi["WeekHours"]:
            hours_of_operation.append("WeekHours - {}".format(poi["WeekHours"]))
        if poi["SaturdayHours"]:
            hours_of_operation.append("SaturdayHours - {}".format(poi["SaturdayHours"]))
        if poi["SundayHours"]:
            hours_of_operation.append("SundayHours - {}".format(poi["SundayHours"]))
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

        if location_name not in scraped_items:
            scraped_items.append(location_name)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
