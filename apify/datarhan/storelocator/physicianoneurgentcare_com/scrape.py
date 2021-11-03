import re
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

    DOMAIN = "physicianoneurgentcare.com"
    start_url = "https://physicianoneurgentcare.com/find-us/locations/"
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36"
    }

    response = session.get(start_url, headers=headers)
    dom = etree.HTML(response.text)

    all_poi = dom.xpath("//div[@data-map-id]")
    for poi_html in all_poi:
        store_url = poi_html.xpath('.//a[@class="center-info-little-link"]/@href')
        store_url = store_url[0] if store_url else "<MISSING>"
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        data = loc_dom.xpath('//script[contains(text(), "wpslMap_0 = ")]/text()')[0]
        data = re.findall(" wpslMap_0 =(.+?);", data)[0]
        data = json.loads(data)

        location_name = data["locations"][0]["store"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = data["locations"][0]["address"]
        city = data["locations"][0]["city"]
        state = data["locations"][0]["state"]
        zip_code = data["locations"][0]["zip"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = data["locations"][0]["country"]
        store_number = data["locations"][0]["id"]
        phone = loc_dom.xpath('//div[@class="location-phone"]/text()')
        phone = phone[0].split(":")[-1].strip() if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = data["locations"][0]["lat"]
        longitude = data["locations"][0]["lng"]
        hours_of_operation = loc_dom.xpath(
            '//h5[contains(text(), "Office")]/following-sibling::ul[1]//text()'
        )
        hours_of_operation = [
            elem.strip() for elem in hours_of_operation if elem.strip()
        ]
        hours_of_operation = (
            " ".join(hours_of_operation).strip() if hours_of_operation else "<MISSING>"
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
