import re
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
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []

    DOMAIN = "byrnedairystores.com"
    start_url = "https://byrnedairystores.com/__locations.php"
    formdata = {"cat": "", "count": "", "keyword": ""}

    response = session.post(start_url, data=formdata)
    data = json.loads(response.text)

    for poi in data:
        store_url = "https://byrnedairystores.com/locations/{}".format(poi["url_title"])
        location_name = poi["title"]
        address_raw = etree.HTML(poi["field_id_18"])
        address_raw = address_raw.xpath("//text()")
        address_raw = [elem.strip() for elem in address_raw if elem.strip()]
        street_address = address_raw[0]
        city = address_raw[-1].split(", ")[0]
        state = address_raw[-1].split(", ")[-1].split()[0]
        zip_code = address_raw[-1].split(", ")[-1].split()[-1]

        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = loc_dom.xpath('//div[@class="location-button"]/a[1]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        location_type = location_type if location_type else "<MISSING>"
        latitude = poi["field_id_54"]
        longitude = poi["field_id_55"]
        hours_of_operation = re.findall('class="hours"><p>(.+?)<', loc_response.text)
        hours_of_operation = (
            hours_of_operation[0] if hours_of_operation else "<MISSING>"
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
