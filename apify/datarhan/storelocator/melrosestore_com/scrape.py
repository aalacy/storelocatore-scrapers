import re
import json
import demjson
import csv
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

    DOMAIN = "melrosestore.com"
    start_url = "https://melrosestore.com/storelocator/"
    response = session.get(start_url)
    dom = etree.HTML(response.text)

    data = dom.xpath('//script[contains(text(), "amLocator")]/text()')[0]
    data = re.findall(r"amLocator\((.+)\);", data.replace("\n", ""))[0]
    data = demjson.decode(data.split(");")[0])

    for poi in data["jsonLocations"]["items"]:
        store_url = "https://melrosestore.com/storelocator/" + poi["url_key"]
        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["address"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["city"]
        city = city if city else "<MISSING>"
        poi_html = etree.HTML(poi["store_list_html"])
        state = poi_html.xpath(
            './/div[@class="amlocator-description"]/following-sibling::text()'
        )
        state = state[1].strip().split(",")[-1].split()[0] if state else "<MISSING>"
        zip_code = poi["zip"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["country"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["id"]
        store_number = store_number if store_number else "<MISSING>"
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["lat"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["lng"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = []
        if poi["schedule_string"]:
            for day, hours in json.loads(poi["schedule_string"]).items():
                opens = "{}:{}".format(hours["from"]["hours"], hours["from"]["minutes"])
                closes = "{}:{}".format(hours["to"]["hours"], hours["to"]["minutes"])
                hours_of_operation.append(f"{day} {opens} - {closes}")
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
