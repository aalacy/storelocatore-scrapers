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

    start_url = "https://www.thebetterhealthstore.com/pointofsale/"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="place US"]')
    for poi_html in all_locations:
        store_url = poi_html.xpath(".//a/@href")
        store_url = store_url[1] if store_url else "<MISSING>"
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = poi_html.xpath(".//h3/a/text()")
        location_name = location_name[0].strip() if location_name else "<MISSING>"
        raw_data = poi_html.xpath('.//div[@class="details"]/text()')
        raw_data = [e.strip() for e in raw_data if e.strip()]
        addr = parse_address_intl(raw_data[0])
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        street_address = street_address if street_address else "<MISSING>"
        city = addr.city
        city = city if city else "<MISSING>"
        state = addr.state
        state = state if state else "<MISSING>"
        zip_code = addr.postcode
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = addr.country
        country_code = country_code if country_code else "<MISSING>"
        store_number = "<MISSING>"
        phone = raw_data[-1][2:]
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hoo = []
        geo = (
            loc_dom.xpath("//iframe/@src")[-1].split("ll=")[-1].split("&")[0].split(",")
        )
        if len(geo) == 2:
            latitude = geo[0]
            longitude = geo[1]
        else:
            geo = (
                loc_dom.xpath('//a[contains(@href, "/maps/")]/@href')[0]
                .split("/@")[-1]
                .split(",")[:2]
            )
            latitude = geo[0]
            longitude = geo[1]
        hoo = [e for e in loc_dom.xpath("//p/text()") if "Hours:" in e]
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = hoo[0].split("Hours:")[-1].strip() if hoo else "<MISSING>"

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
