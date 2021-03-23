import re
import csv
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

    start_url = "https://www.jacksurbaneats.com/locations/"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[h2[contains(text(), "Hours")]]')
    for poi_html in all_locations:
        store_url = start_url
        location_name = poi_html.xpath(".//h1/text()")
        if not location_name:
            continue
        location_name = location_name[0]
        street_address = poi_html.xpath(".//p/a/text()")
        street_address = street_address[0] if street_address else "<MISSING>"
        city = poi_html.xpath(".//p/text()")[-1].split(", ")[0].strip()
        state = poi_html.xpath(".//p/text()")[-1].split(", ")[-1].split()[0].strip()
        zip_code = poi_html.xpath(".//p/text()")[-1].split(", ")[-1].split()[-1].strip()
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = poi_html.xpath('.//a[contains(@href, "tel")]/text()')
        if not phone:
            all_text = poi_html.xpath(".//text()")
            all_text = [e.strip() for e in all_text if e.strip()]
            phone = [e for e in all_text if e.startswith("(")]
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        geo = poi_html.xpath('.//a[contains(@href, "maps")]/@href')[0]
        if "/@" in geo:
            geo = geo.split("/@")[-1].split(",")[:2]
            latitude = geo[0]
            longitude = geo[1]
        hoo = poi_html.xpath(
            './/h2[contains(text(), "Hours")]/following-sibling::p//text()'
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
