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

    start_url = "https://redhedoil.com/locations/"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//table[@style="width: 720px; height: 665px;"]/tbody/tr/td[@width!="1"]'
    )
    for poi_html in all_locations:
        store_url = start_url
        raw_data = poi_html.xpath(".//text()")
        raw_data = [e.strip() for e in raw_data if e.strip() and "(" not in e]
        if not raw_data:
            continue
        location_name = raw_data[0]
        street_address = raw_data[1]
        city = raw_data[2].split(", ")[0]
        city = city if city else "<MISSING>"
        state = raw_data[2].split(", ")[-1].split()[0]
        zip_code = raw_data[2].split(", ")[-1].split()[-1]
        country_code = "<MISSING>"
        store_number = location_name.split("#")[-1].strip().split("/")[0].strip()
        phone = poi_html.xpath(".//text()")[-2].strip()
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
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
