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

    start_url = (
        "http://qiknez.com/wp-content/plugins/superstorefinder-wp/ssf-wp-xml.php"
    )
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    response = session.get("http://qiknez.com/locations/")
    dom = etree.HTML(response.text)
    hoo = dom.xpath(
        '//div[h2[contains(text(), "OPERATING HOURS")]]/following-sibling::div[1]//text()'
    )
    hoo = [e.strip() for e in hoo if e.strip()]
    hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath("//item")
    for poi_html in all_locations:
        store_url = "http://qiknez.com/locations/"
        location_name = poi_html.xpath(".//location/text()")[0]
        raw_address = poi_html.xpath(".//address/text()")[0]
        addr = parse_address_intl(raw_address)

        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        city = addr.city
        state = addr.state
        zip_code = addr.postcode
        country_code = "<MISSING>"
        store_number = poi_html.xpath(".//storeid/text()")[0]
        phone = poi_html.xpath(".//telephone/text()")
        phone = phone[0] if phone else "<MISSING>"
        location_type = poi_html.xpath(".//productsservices/text()")[0]
        latitude = poi_html.xpath(".//latitude/text()")[0]
        longitude = poi_html.xpath(".//longitude/text()")[0]

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
