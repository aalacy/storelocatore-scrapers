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

    DOMAIN = "pitajungle.com"
    start_url = "https://www.pitajungle.com/block/ajax/map/ajax_get_locations"

    formdata = {
        "address": "",
        "distance": "5",
        "latitude": "",
        "longitude": "",
        "delivery": "",
    }
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }
    response = session.post(start_url, data=formdata, headers=headers)
    data = json.loads(response.text)

    for poi in data:
        store_url = poi["schemaEmbed"]["url"]
        store_url = store_url if store_url else "<MISSING>"
        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["schemaEmbed"]["address"]["streetAddress"].split(
            "Terminal"
        )[0]
        city = poi["schemaEmbed"]["address"]["addressLocality"]
        state = poi["schemaEmbed"]["address"]["addressRegion"]
        zip_code = poi["schemaEmbed"]["address"]["postalCode"]
        phone = poi["phoneNumber"]
        phone = phone if phone else "<MISSING>"
        country_code = poi["schemaEmbed"]["address"]["addressCountry"]
        store_number = poi["id"]
        location_type = poi["schemaEmbed"]["@type"]
        latitude = poi["latitude"]
        longitude = poi["longitude"]
        hoo = ""
        if poi["hours"]:
            hoo = etree.HTML(poi["hours"])
            hoo = hoo.xpath("//text()")
            hoo = [elem.strip() for elem in hoo if elem.strip()]
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

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
