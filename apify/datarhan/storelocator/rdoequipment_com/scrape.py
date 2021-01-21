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

    DOMAIN = "rdoequipment.com"
    start_url = "https://www.rdoequipment.com/api/locations?industryId=&lat=40.75368539999999&lng=-73.9991637&locationType=&radius=5000"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36",
    }

    response = session.get(start_url, headers=headers)
    data = json.loads(response.text)

    for poi in data:
        store_url = (
            "https://www.rdoequipment.com/more/locations/location" + poi["detailURL"]
        )
        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["address"]["street"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["address"]["city"].replace(",", "").strip()
        city = city if city else "<MISSING>"
        state = poi["address"]["stateCode"]
        state = state if state else "<MISSING>"
        zip_code = poi["address"]["zip"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["address"]["countryCode"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = "<MISSING>"
        phone = poi["phoneNumber"]
        phone = phone if phone else "<MISSING>"
        location_type = [elem["text"] for elem in poi["locationTypes"]]
        location_type = ", ".join(location_type) if location_type else "<MISSING>"
        latitude = poi["address"]["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["address"]["longitude"]
        longitude = longitude if longitude else "<MISSING>"

        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        hours_of_operation = loc_dom.xpath('//table[@id="allweekhours_sales"]//text()')
        hours_of_operation = [
            elem.strip() for elem in hours_of_operation if elem.strip()
        ]
        hours_of_operation = (
            " ".join(hours_of_operation).replace("Days Hours ", "")
            if hours_of_operation
            else "<MISSING>"
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
