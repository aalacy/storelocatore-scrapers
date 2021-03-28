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

    start_url = "https://kidsandcompany.com/locations-across-canada/"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="location-item"]')
    for poi_html in all_locations:
        store_url = poi_html.xpath(".//a/@href")[0]
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        raw_data = loc_dom.xpath(
            '//h4[contains(text(), "Address")]/following-sibling::p/text()'
        )

        location_name = raw_data[0]
        location_name = location_name if location_name else "<MISSING>"
        street_address = raw_data[1]
        street_address = street_address if street_address else "<MISSING>"
        city = raw_data[2].split(", ")[0]
        state = raw_data[2].split(", ")[1]
        zip_code = raw_data[2].split(", ")[-1]
        country_code = "CA"
        store_number = "<MISSING>"
        phone = raw_data[3]
        location_type = "<MISSING>"
        latitude = loc_dom.xpath("//@data-lat")
        latitude = latitude[0] if latitude else "<MISSING>"
        longitude = loc_dom.xpath("//@data-lng")
        longitude = longitude[0] if longitude else "<MISSING>"
        hoo = loc_dom.xpath(
            '//h4[contains(text(), "Centre Hours")]/following-sibling::p[1]/text()'
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
