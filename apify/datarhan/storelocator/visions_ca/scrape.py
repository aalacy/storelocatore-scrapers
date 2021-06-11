import re
import csv
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl


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

    start_url = "https://www.visions.ca/StoreLocator/Default.aspx"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="storelocator-container"]')
    for poi_html in all_locations:
        store_url = start_url
        location_name = poi_html.xpath(
            './/div[@class="storelocator-body"]/span[@class="storelocator-city"]/text()'
        )
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_data = poi_html.xpath('.//div[@class="storelocator-body"]/text()')
        raw_data = [e.strip() for e in raw_data if e.strip()]
        raw_address = []
        for elem in raw_data:
            if "Phone" in elem:
                break
            raw_address.append(elem)
        addr = parse_address_intl(" ".join(raw_address))
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        city = addr.city
        state = addr.state
        if state.endswith("."):
            state = state[:-1]
        zip_code = addr.postcode
        country_code = addr.country
        country_code = country_code if country_code else "<MISSING>"
        store_number = "<MISSING>"
        phone = [e for e in raw_data if "Phone" in e]
        phone = phone[0].split(":")[-1] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        geo = poi_html.xpath(
            './/following-sibling::div[@class="storelocator-map"][1]//a/@href'
        )[0]
        if "/@" in geo:
            geo = geo.split("/@")[-1].split(",")[:2]
            latitude = geo[0]
            longitude = geo[1]
        hoo = poi_html.xpath(
            './/div[@class="storelocator-hours"]/div[@class="storelocator-body"]/text()'
        )
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

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
