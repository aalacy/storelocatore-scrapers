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

    DOMAIN = "dentalworks.com"
    start_url = (
        "https://www.dentalworks.com/wp-content/uploads/office-data/all-offices.json"
    )
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/8.0.4280.67 Safari/537.36"
    }
    response = session.get(start_url, headers=headers)
    data = json.loads(response.text)

    for poi in data["features"]:
        store_url = poi["properties"]["permalink"]
        store_response = session.get(store_url + "our-location/", headers=headers)
        store_dom = etree.HTML(store_response.text)
        hoo = store_dom.xpath('//div[@class="location__hours"]//text()')
        hoo = [elem.strip() for elem in hoo if elem.strip()]
        hours_of_operation = ", ".join(hoo) if hoo else "<MISSING>"

        location_name = poi["properties"]["name"]
        location_name = location_name if location_name else "<MISSING>"
        address_raw = (
            poi["properties"]["address"].replace("\r\n", ", ").replace(", USA", "")
        )
        address_raw = address_raw.split(",")
        address_raw = [elem.strip() for elem in address_raw]
        if len(address_raw) > 4:
            address_raw = address_raw[:4]
        if len(address_raw) == 4:
            address_raw = [", ".join(address_raw[:2])] + address_raw[2:]
        street_address = address_raw[0].replace(",", "")
        if len(address_raw[1].strip().split()[0]) == 2:
            city = "<MISSING>"
            state = address_raw[1].split()[0]
            zip_code = address_raw[1].split()[-1]
        else:
            city = address_raw[1].strip()
            state = address_raw[2].split()[0]
            zip_code = address_raw[2].split()[-1]
        country_code = "<MISSING>"
        store_number = poi["properties"]["id"]
        phone = poi["properties"]["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["geometry"]["coordinates"][1]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["geometry"]["coordinates"][0]
        longitude = longitude if longitude else "<MISSING>"

        if len(zip_code.strip()) == 2:
            zip_code = "<MISSING>"
        if city == "<MISSING>":
            city = street_address.split()[-1]
            street_address = " ".join(street_address.split()[:-1])
        if zip_code == "<MISSING>":
            zip_code = store_dom.xpath('//div[@class="location__addy"]/p/text()')[
                2
            ].split()[-1]

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
