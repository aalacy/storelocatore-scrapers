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

    start_url = "https://www.super-saver.com/connect-with-us/"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//div[@class="entry-content"]/div[@class="vc_row wpb_row vc_row-fluid"]'
    )[1:]
    for poi_html in all_locations:
        store_url = poi_html.xpath(".//h3/a/@href")
        if not store_url:
            continue
        store_url = store_url[0]
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = poi_html.xpath(".//h3/a/text()")
        location_name = location_name[0].strip() if location_name else "<MISSING>"
        raw_address = poi_html.xpath('.//p[contains(text(), "Store Director")]/text()')[
            1:3
        ]
        raw_address = [e.strip() for e in raw_address if e.strip()]
        if not raw_address:
            raw_address = poi_html.xpath(
                './/*[contains(text(), "Store Director")]/following-sibling::*//text()'
            )[:2]
        if not raw_address:
            continue
        street_address = raw_address[0].strip()
        city = raw_address[1].split(", ")[0].strip()
        state = raw_address[1].split(", ")[-1].split()[0].strip()
        zip_code = raw_address[1].split(", ")[-1].split()[-1].strip()
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        try:
            phone = (
                poi_html.xpath('.//p[contains(text(), "Store Director")]/text()')[3]
                .split(":")[-1]
                .strip()
            )
        except:
            phone = (
                poi_html.xpath(
                    './/*[contains(text(), "Store Director")]/following-sibling::*//text()'
                )[2]
                .split(":")[-1]
                .strip()
            )
        location_type = "<MISSING>"
        geo = (
            loc_dom.xpath('//a[contains(@href, "/maps/")]/@href')[0]
            .split("/@")[-1]
            .split(",")[:2]
        )
        latitude = geo[0]
        longitude = geo[1]
        hours_of_operation = poi_html.xpath(".//text()")
        hours_of_operation = [e for e in hours_of_operation if "Open 24" in e]
        hours_of_operation = (
            hours_of_operation[0].strip() if hours_of_operation else "<MISSING>"
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
