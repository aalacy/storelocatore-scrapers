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

    start_url = "https://www.fields.ca/pointofsale"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="place CA"]')
    for poi_html in all_locations:
        store_url = start_url
        location_name = poi_html.xpath(".//a[@id]/text()")
        location_name = location_name[0].strip() if location_name else "<MISSING>"
        raw_data = poi_html.xpath('.//div[@class="details"]/text()')
        raw_data = [e.strip() for e in raw_data if e.strip()]
        addr = parse_address_intl(" ".join(raw_data[:3]))
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        street_address = street_address if street_address else "<MISSING>"
        if street_address == "260":
            street_address += " City Centre"
        city = addr.city
        if not city:
            city = location_name
        city = city.replace("Canada", "")
        state = addr.state
        state = state if state else "<MISSING>"
        zip_code = addr.postcode
        zip_code = zip_code if zip_code else "<MISSING>"
        if len(zip_code.split()) > 2:
            city = " ".join(zip_code.split()[2:])
            zip_code = " ".join(zip_code.split()[:2])
        if len(zip_code.strip()) == 3:
            zip_code = zip_code + " " + street_address.split()[-1]
            street_address = " ".join(street_address.split()[:-1])
        country_code = "Canada"
        store_number = poi_html.xpath(".//a/@id")
        store_number = store_number[0] if store_number else "<MISSING>"
        phone = raw_data[3].strip()[1:]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hoo = poi_html.xpath('.//div[@class="details"]/p/text()')
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
