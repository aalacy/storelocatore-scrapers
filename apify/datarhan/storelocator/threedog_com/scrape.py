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
    items = []

    session = SgRequests()

    DOMAIN = "theparkingspot.com"
    start_url = "https://threedog.com/wp/wp-admin/admin-ajax.php?location=Kansas+City%2C+MO&tdb_nonce={}&action=get_bakeries_json"

    response = session.get("https://threedog.com/")
    token = re.findall("nonce: '(.+?)',", response.text)[0]
    response = session.get(start_url.format(token), verify=False)
    data = json.loads(response.text)

    for poi in data["results"]:
        poi_html = etree.HTML(poi["html"])
        store_url = poi_html.xpath('//a[contains(@href, "threedog.com")]/@href')
        store_url = store_url[0] if store_url else "<MISSING>"
        location_name = poi_html.xpath("//h3/text()")
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_address = poi_html.xpath('//div[@class="address"]/text()')
        raw_address = [elem.strip() for elem in raw_address if elem.strip()]
        street_address = raw_address[0]
        city = raw_address[-1].split(", ")[0]
        state = raw_address[-1].split(", ")[-1].split()[0]
        if "Hong" in state:
            continue
        zip_code = raw_address[-1].split(", ")[-1].split()[-1]
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = poi_html.xpath('//a[contains(@href, "tel")]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["longitude"]
        longitude = longitude if longitude else "<MISSING>"

        loc_response = session.get(store_url, verify=False)
        loc_dom = etree.HTML(loc_response.text)
        hoo = loc_dom.xpath('//div[@class="hours"]/text()')
        hoo = [elem.strip() for elem in hoo if elem.strip()]
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"
        if "Coming Soon" in hours_of_operation:
            location_type = "Coming Soon"

        if "Canada" in raw_address[-1]:
            city = raw_address[-1].split(", ")[0]
            state = raw_address[-1].split(", ")[1]
            zip_code = " ".join(raw_address[-1].split(", ")[-1].split()[-2:])
            country_code = "Canada"

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
