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

    start_url = "https://thegreatmaple.com/"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//a[@title="Locations"]/following-sibling::ul/li/a/@href'
    )
    for store_url in list(set(all_locations)):
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath("//h1/strong/span/text()")
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_address = loc_dom.xpath(
            '//h3[strong[span[contains(text(), "ADDRESS")]]]/following-sibling::p/span/text()'
        )
        if not raw_address:
            raw_address = loc_dom.xpath(
                '//h3[strong[span[contains(text(), "ADDRESS")]]]/following-sibling::p/text()'
            )
        if not raw_address:
            raw_address = loc_dom.xpath(
                '//h4[span[strong[span[contains(text(), "ADDRESS")]]]]/following-sibling::p[1]/text()'
            )
        if not raw_address:
            raw_address = loc_dom.xpath(
                '//h4[span[strong[contains(text(), "ADDRESS")]]]/following-sibling::p[1]/span/text()'
            )[1:]
        street_address = raw_address[0]
        city = raw_address[1].split(", ")[0]
        state = raw_address[1].split(", ")[-1].split()[0]
        zip_code = raw_address[1].split(", ")[-1].split()[-1]
        country_code = "US"
        store_number = "<MISSING>"
        phone = raw_address[-1]
        location_type = "<MISSING>"
        latitude = loc_dom.xpath("//div/@data-latitude")[0]
        longitude = loc_dom.xpath("//div/@data-longitude")[0]
        hoo = loc_dom.xpath(
            '//h3[strong[span[contains(text(), "HOURS")]]]/following-sibling::*[1]//text()'
        )
        if not hoo:
            hoo = loc_dom.xpath(
                '//h4[span[strong[span[contains(text(), "HOURS")]]]]/following-sibling::*[1]//text()'
            )
        if not hoo:
            hoo = loc_dom.xpath(
                '//h4[span[strong[contains(text(), "HOURS")]]]/following-sibling::*[1]//text()'
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
