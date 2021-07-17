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

    start_url = "https://www.leons.ca/apps/store-locator"
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
        poi_html = (
            poi["address"]
            .replace("&lt;", "<")
            .replace("&quot;", '"')
            .replace("&gt;", ">")
            .replace("&#039;", '"')
        )
        poi_html = etree.HTML(poi_html)

        store_url = start_url
        location_name = poi_html.xpath('//span[@class="name"]/text()')
        location_name = location_name[0].strip() if location_name else "<MISSING>"
        street_address = poi_html.xpath('//span[@class="address"]/text()')
        street_address = street_address[0].strip() if street_address else "<MISSING>"
        city = poi_html.xpath('//span[@class="city"]/text()')
        city = city[0].strip() if city else "<MISSING>"
        state = poi_html.xpath('//span[@class="prov_state"]/text()')
        state = state[0].strip() if state else "<MISSING>"
        zip_code = poi_html.xpath('//span[@class="postal_zip"]/text()')
        zip_code = zip_code[0] if zip_code else "<MISSING>"
        country_code = poi_html.xpath('//span[@class="country"]/text()')
        country_code = country_code[0].strip() if country_code else "<MISSING>"
        store_number = poi["id"]
        phone = poi_html.xpath('//span[@class="phone"]/text()')
        phone = phone[0].strip() if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["lat"]
        longitude = poi["lng"]
        hoo = poi_html.xpath('//span[@class="hours"]/text()')
        if "Temporarily Closed" in hoo[0]:
            location_type = "Temporarily Closed"
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo).split("Hours:")[-1] if hoo else "<MISSING>"

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
