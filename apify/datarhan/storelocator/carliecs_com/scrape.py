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

    DOMAIN = "carliecs.com"
    start_url = "https://api.freshop.com/1/stores?app_key=carlie_c_s&has_address=true&limit=-1&token=9c9540059bb21c601480bb087a51ff4b"

    response = session.get(start_url)
    data = json.loads(response.text)

    for poi in data["items"]:
        store_url = poi["url"]
        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["address_1"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["city"]
        state = poi["state"]
        zip_code = poi["postal_code"]
        country_code = "<MISSING>"
        store_number = poi["number"]
        phone = poi["phone_md"].split("\n")[0].strip()
        location_type = "<MISSING>"
        hoo = []
        if poi.get("delivery_areas"):
            try:
                latitude = poi["delivery_areas"][-1]["lat_lng"][0][0]
                longitude = poi["delivery_areas"][-1]["lat_lng"][0][-1]
            except Exception:
                areas = poi["delivery_areas"]
                latitude = [elem["lat_lng"] for elem in areas if elem.get("lat_lng")][
                    0
                ][0][0]
                longitude = [elem["lat_lng"] for elem in areas if elem.get("lat_lng")][
                    0
                ][0][-1]
        hoo = poi["hours_md"].replace("\n", " ").split("Senior")[0].strip()
        hours_of_operation = hoo if hoo else "<MISSING>"

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
