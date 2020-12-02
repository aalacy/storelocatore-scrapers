import re
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
    DOMAIN = "orangejulius.com"
    session = SgRequests()

    items = []
    scraped_items = []

    start_url = "https://webapi.dairyqueen.com/v3/store/locator?callback=jQuery111304643188529110178_1606299141114&latitude=40.75368539999999&longitude=-73.9991637&radius=50000&mallMenu=true&conditions=dairy_queen"
    response = session.get(start_url)
    data = re.findall(r".+\d+\((.+)\)", response.text)[0]
    data = json.loads(data)

    for poi in data:
        store_url = "<MISSING>"
        location_name = poi["address"]["store_name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["address"]["street_address"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["address"]["city"]
        city = city if city else "<MISSING>"
        state = poi["address"]["state_province_abbr"]
        state = state if state else "<MISSING>"
        zip_code = poi["address"]["postal_code"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["address"]["country_abbr"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["store_no"]
        phone = poi["phone_number"]
        phone = phone if phone else "<MISSING>"
        location_type = ""
        location_type = location_type if location_type else "<MISSING>"
        latitude = poi["geo_data"]["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["geo_data"]["longitude"]
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
        if location_name not in scraped_items:
            scraped_items.append(location_name)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
