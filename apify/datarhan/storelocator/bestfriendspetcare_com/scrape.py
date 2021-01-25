import csv
import json
from lxml import etree
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

    DOMAIN = "bestfriendspetcare.com"
    start_url = (
        "https://cms.bestfriendspetcare.com/wp-json/cache/v1/locations-by-state/all"
    )

    response = session.get(start_url)
    data = json.loads(response.text)

    for state in data.keys():
        locations = data[state]["locations"]

        for poi in locations:
            store_url = f'https://www.bestfriendspetcare.com/location/{poi["value"]}'
            location_name = poi["label"]
            location_name = location_name if location_name else "<MISSING>"
            street_address = poi["address"]["line1"]
            if poi["address"]["line2"]:
                street_address += ", " + poi["address"]["line2"]
            street_address = street_address if street_address else "<MISSING>"
            city = poi["address"]["city"]
            city = city if city else "<MISSING>"
            state = poi["address"]["state"]
            state = state if state else "<MISSING>"
            zip_code = poi["address"]["zip"]
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = "<MISSING>"
            store_number = poi["id"]
            phone = poi["phone"]
            phone = phone if phone else "<MISSING>"
            location_type = "<MISSING>"
            latitude = poi["lat"]
            latitude = latitude if latitude else "<MISSING>"
            longitude = poi["lng"]
            longitude = longitude if longitude else "<MISSING>"
            hoo = etree.HTML(poi["hours"])
            hoo = [elem.strip() for elem in hoo.xpath("//text()") if "AM" in elem]
            hours_of_operation = ", ".join(hoo) if hoo else "<MISSING>"

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
