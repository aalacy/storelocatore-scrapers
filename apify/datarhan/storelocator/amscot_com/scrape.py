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

    DOMAIN = "amscot.com"
    start_url = "https://www.amscot.com/handlers/pinsNearestAms.ashx?city1=altamonte+springs&lat1=28.665015750000002&lon1=-81.38724625&range=20000"

    response = session.get(start_url)
    data = json.loads(response.text)

    for poi in data:
        location_name = poi["BRANCHNAME"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["ADDRESS"]
        if poi["ADDRESS2"]:
            street_address += ", " + poi["ADDRESS2"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["CITY"]
        city = city if city else "<MISSING>"
        state = poi["STATE"]
        state = state if state else "<MISSING>"
        zip_code = poi["ZIP"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["LID"]
        phone = poi["PHONE"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        if poi["COMINGSOON"]:
            location_type = "COMINGSOON"
        latitude = poi["LATITUDE"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["LONGITUDE"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = poi["HOURS"]

        store_url = "https://www.amscot.com/location/branch-{}/{}-{}-{}-{}"
        store_url = store_url.format(
            str(store_number),
            street_address.replace(" ", "-").replace(".", ""),
            city.replace(" ", "-"),
            state,
            zip_code,
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
