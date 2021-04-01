import re
import csv
import demjson
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

    start_url = "https://us.aritaum.com/apps/store-locator"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    all_locations = re.findall(r"Coords.push\((.+?)\);", response.text)

    for poi in all_locations:
        try:
            poi = demjson.decode(poi)
        except:
            continue
        store_url = start_url
        poi_html = etree.HTML(
            poi["address"]
            .replace("&lt;", "<")
            .replace("&gt;", ">")
            .replace("&#039;", '"')
        )
        location_name = poi_html.xpath('//span[@class="name"]/text()')
        location_name = location_name[0].strip() if location_name else "<MISSING>"
        street_address = poi_html.xpath('//span[@class="address"]/text()')[0]
        if poi_html.xpath('//span[@class="address2"]/text()'):
            street_address += (
                " " + poi_html.xpath('//span[@class="address2"]/text()')[0]
            )
        street_address = street_address.strip() if street_address else "<MISSING>"
        city = poi_html.xpath('//span[@class="city"]/text()')
        city = city[0].strip() if city else "<MISSING>"
        state = poi_html.xpath('//span[@class="prov_state"]/text()')
        state = state[0].strip() if state else "<MISSING>"
        zip_code = poi_html.xpath('//span[@class="postal_zip"]/text()')
        zip_code = zip_code[0].strip() if zip_code else "<MISSING>"
        country_code = poi_html.xpath('//span[@class="country"]/text()')
        country_code = country_code[0] if country_code else "<MISSING>"
        store_number = poi["id"]
        phone = "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["lat"]
        longitude = poi["lng"]
        hours_of_operation = "<MISSING>"

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
