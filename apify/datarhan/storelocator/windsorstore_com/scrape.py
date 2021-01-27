import json
import csv
import urllib.parse
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
    session = SgRequests().requests_retry_session(retries=0, backoff_factor=0.3)

    items = []

    DOMAIN = "windsorstore.com"
    start_url = (
        "https://cdn.shopify.com/s/files/1/0070/8853/7651/t/8/assets/stores.json"
    )

    response = session.get(start_url)
    data = json.loads(response.text)

    for poi in data["features"]:
        store_url = "https://www.windsorstore.com" + poi["properties"]["url"]
        location_name = poi["properties"]["name"]
        if location_name == "zebra test location":
            continue
        if "Coming" in location_name:
            continue
        street_address = poi["properties"]["street_1"]
        if poi["properties"]["street_2"]:
            street_address += ", " + poi["properties"]["street_2"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["properties"]["city"]
        state = poi["properties"]["state"]
        zip_code = poi["properties"]["zip"]
        country_code = "<MISSING>"
        store_number = poi["properties"]["store_number"]
        store_number = store_number if store_number else "<MISSING>"
        phone = poi["properties"]["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["geometry"]["coordinates"][0]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["geometry"]["coordinates"][-1]
        longitude = longitude if longitude else "<MISSING>"

        store_response = session.get(store_url)
        store_dom = etree.HTML(store_response.text)
        hours_of_operation = store_dom.xpath(
            '//div[@class="StoreDetail__hours"]/@data-store-hours'
        )
        hours_of_operation = (
            urllib.parse.unquote(hours_of_operation[0]) if hours_of_operation else ""
        )
        hoo = []
        if hours_of_operation:
            hours_of_operation = json.loads(hours_of_operation)
            hours_of_operation = hours_of_operation if hours_of_operation else []
            for elem in hours_of_operation:
                hoo.append(f'{elem["day"]} {elem["hours"]}')
        hours_of_operation = " ".join(hoo).replace("+", " ") if hoo else "<MISSING>"

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
