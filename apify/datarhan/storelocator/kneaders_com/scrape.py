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

    DOMAIN = "kneaders.com"
    start_url = "https://wordpress.kneadersdw.com/wp-json/kneaders/v1/locations/{}"

    all_locations = []
    states = ["AZ", "ID", "NV", "TX", "UT", "CO"]
    for state in states:
        response = session.get(start_url.format(state))
        data = json.loads(response.text)
        all_locations += data["rows"]

    for poi in all_locations:
        store_url = poi["menu_url"]
        store_url = store_url if store_url else "<MISSING>"
        location_name = poi["title"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["address"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["city"]
        city = city if city else "<MISSING>"
        state = poi["state"]
        state = state if state else "<MISSING>"
        zip_code = poi["zip"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["geocode"][0]["results"][0]["geometry"]["location"]["lat"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["geocode"][0]["results"][0]["geometry"]["location"]["lng"]
        longitude = longitude if longitude else "<MISSING>"
        hoo_html = etree.HTML(poi["hours"])
        hours_of_operation = [
            elem.strip() for elem in hoo_html.xpath(".//text()") if elem.strip()
        ]
        hours_of_operation = (
            " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
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
