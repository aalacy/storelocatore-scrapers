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

    DOMAIN = "oldtimepottery.com"
    start_url = "https://storerocket.global.ssl.fastly.net/api/user/j9X8R92JAE/locations?lat=40.6331249&lng=-89.3985283&radius=2500"
    response = session.get(start_url)
    data = json.loads(response.text)

    for poi in data["results"]["locations"]:
        store_url = poi["url"]
        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["address"].split("<br>")[0].strip()
        street_address = street_address if street_address else "<MISSING>"
        city = poi["city"]
        city = city if city else "<MISSING>"
        state = poi["state"]
        state = state if state else "<MISSING>"
        zip_code = poi["postcode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["country"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["marker_id"]
        store_number = store_number if store_number else "<MISSING>"
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = poi["location_type_name"]
        latitude = poi["lat"]
        longitude = poi["lng"]

        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        hours_of_operation = loc_dom.xpath(
            '//div[@class="hours"]/div[@class="footer"]/p[1]/span/text()'
        )
        hours_of_operation += loc_dom.xpath(
            '//div[@class="hours"]/div[@class="footer"]/p[2]/span/text()'
        )
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
