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

    start_url = "https://sammoon.com/pages/locations"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="backpage-content"]/table')
    for poi_html in all_locations:
        store_url = start_url
        location_name = poi_html.xpath(".//td/h3/text()")
        location_name = location_name[0].strip() if location_name else "<MISSING>"
        raw_data = poi_html.xpath(".//tr[1]/td[1]/p[1]/text()")
        if len(raw_data) == 4:
            raw_data = [" ".join(raw_data[:2])] + raw_data[2:]
        street_address = raw_data[0][:-1]
        city = raw_data[1].split(", ")[0]
        state = raw_data[1].split(", ")[-1].split()[0]
        zip_code = raw_data[1].split(", ")[-1].split()[-1]
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = raw_data[-1].split(":")[-1].strip()
        location_type = "<MISSING>"
        geo = poi_html.xpath(".//following-sibling::iframe[1]/@src")
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        if geo:
            geo = geo[0].split("!2d")[-1].split("!2m")[0].split("!3d")
            latitude = geo[-1]
            longitude = geo[0]
        hoo = poi_html.xpath(".//tr[1]/td[1]/p[2]//text()")
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
