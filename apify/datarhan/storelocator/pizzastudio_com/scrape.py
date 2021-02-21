import csv
import json
from lxml import etree

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
    items = []

    session = SgRequests()

    DOMAIN = "pizzastudio.com"
    start_url = "https://pizzastudio.com/stores.json"

    response = session.get(start_url)
    data = json.loads(response.text)

    for poi in data:
        store_url = "https://pizzastudio.com/locations/" + poi["locationurl"]
        location_name = poi["locationname"]
        street_address = poi.get("address1")
        if not street_address:
            continue
        city = poi["city"]
        state = poi["stateabbrev"]
        if len(state) != 2:
            continue
        if poi["state"] == "Canada":
            continue
        if state == "BR":
            continue
        zip_code = poi.get("zip")
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = poi.get("phone")
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["lat"]
        longitude = poi["lon"]
        hoo = etree.HTML(poi["hours"])
        hoo = [elem.strip() for elem in hoo.xpath(".//text()") if elem.strip]
        hours_of_operation = " ".join(hoo).split("Start")[0] if hoo else "<MISSING>"
        hours_of_operation = hours_of_operation.replace("Catering Options", "")
        hours_of_operation = (
            hours_of_operation.split("Sign")[0]
            .split("Click")[0]
            .replace(" Delivery Available", "")
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
