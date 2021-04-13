import re
import csv
import json
from urllib.parse import urljoin
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
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []

    start_url = "https://www.elriogrande.net/store-locator/json"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    data = json.loads(response.text)

    for poi in data["features"]:
        if not poi:
            continue
        store_url = urljoin(start_url, poi["properties"]["path_rendered"])
        location_name = poi["properties"]["name"]
        location_name = location_name if location_name else "<MISSING>"
        poi_html = etree.HTML(poi["properties"]["description"])
        street_address = poi_html.xpath('//div[@class="thoroughfare"]/text()')
        street_address = street_address[0] if street_address else "<MISSING>"
        city = poi_html.xpath('//span[@class="locality"]/text()')
        city = city[0] if city else "<MISSING>"
        state = poi_html.xpath('//span[@class="state"]/text()')
        state = state[0] if state else "<MISSING>"
        zip_code = poi_html.xpath('//span[@class="postal-code"]/text()')
        zip_code = zip_code[0] if zip_code else "<MISSING>"
        country_code = poi_html.xpath('//span[@class="country"]/text()')
        country_code = country_code[0] if country_code else "<MISSING>"
        store_number = poi["properties"]["nid"]
        phone = poi["properties"]["gsl_props_phone_rendered"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["geometry"]["coordinates"][1]
        longitude = poi["geometry"]["coordinates"][0]
        hours_of_operation = (
            poi["properties"]["gsl_props_misc_rendered"][1:-1]
            .replace("%, ^", ", ")
            .replace("&amp;", "")
        )

        item = [
            domain,
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
