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
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []

    start_url = "https://ramenbannai.com/location/"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="location-box clearfix"]')
    for poi_html in all_locations:
        store_url = start_url
        location_name = poi_html.xpath('.//p/span[@class="tenpo"]/text()')[0].split()
        location_name = [e.strip() for e in location_name if e.strip()]
        location_name = " ".join(location_name).replace("â", "-")
        raw_address = (
            poi_html.xpath('.//*[contains(text(), "Address:")]/text()')[0]
            .strip()
            .split("Address: ")[-1]
        )
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        city = addr.city
        state = addr.state
        zip_code = addr.postcode
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = poi_html.xpath(".//p/text()")[1].split("Phone: ")[-1].strip()
        if not phone:
            phone = poi_html.xpath('.//span[contains(text(), "Phone:")]/text()')[
                0
            ].split(": ")[-1]
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hoo = poi_html.xpath('.//p[@class="p01 hours-text"]/text()')
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = (
            " ".join(hoo).replace("â\x80\x93", "-") if hoo else "<MISSING>"
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
