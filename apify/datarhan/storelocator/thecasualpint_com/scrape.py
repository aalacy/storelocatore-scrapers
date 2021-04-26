import re
import csv
import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_usa


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

    start_url = "https://thecasualpint.com/#"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    data = dom.xpath('//script[contains(text(), "maps(")]/text()')[0]
    data = re.findall(r"maps\((.+?)\).data", data)[0]
    data = json.loads(data)

    for poi in data["places"]:
        poi_html = poi_html = etree.HTML(poi["content"])
        store_url = poi_html.xpath("//a[contains(@href, 'thecasualpint.com')]/@href")[0]
        if "@" in store_url:
            store_url = "https://centralphoenix.thecasualpint.com/beer-selection/"
        location_name = poi["title"]
        location_name = location_name if location_name else "<MISSING>"
        addr = parse_address_usa(poi["address"])
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        street_address = street_address if street_address else "<MISSING>"
        city = poi["location"]["city"]
        city = city.split(",")[-1].strip() if city else "<MISSING>"
        state = poi["location"]["state"]
        state = state if state else "<MISSING>"
        zip_code = poi["location"]["postal_code"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["location"]["country"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["id"]
        phone = [e.strip() for e in poi_html.xpath(".//text()") if "(" in e]
        if not phone:
            loc_response = session.get(store_url, headers=hdr)
            loc_dom = etree.HTML(loc_response.text)
            phone = loc_dom.xpath('//li[@class="phone"]/a/text()')
        phone = phone[0].replace("phone:", "").strip() if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["location"]["lat"]
        longitude = poi["location"]["lng"]
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
