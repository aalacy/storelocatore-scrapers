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

    start_url = "https://cinestarz.ca/"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="menu-footer-en-container"]//li/a/@href')
    for store_url in all_locations:
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//h1[@class="vc_custom_heading"]/text()')
        if not location_name:
            location_name = loc_dom.xpath('//h2[@class="vc_custom_heading"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_data = loc_dom.xpath(
            '//div[@id="contact"]//div[@class="wpb_wrapper"]/p/text()'
        )
        if not raw_data:
            raw_data = loc_dom.xpath(
                '//div[div[contains(text(), "Cine Starz")]]/div/text()'
            )
        raw_data = [e.strip() for e in raw_data if e.strip()]
        addr = parse_address_intl(" ".join(raw_data[:-1]))
        if "cine starz" in raw_data[0].lower():
            raw_data = raw_data[1:]
        street_address = raw_data[0]
        if street_address.endswith(","):
            street_address = street_address[:-1]
        city = addr.city
        state = addr.state
        if state.endswith("."):
            state = state[:-1]
        zip_code = addr.postcode.split("PHONE")[0].strip()
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = raw_data[-1].split(":")[-1].strip()
        location_type = "<MISSING>"
        geo = (
            loc_dom.xpath("//iframe/@src")[0].split("ll=")[-1].split("&")[0].split(",")
        )
        if len(geo) == 2:
            latitude = geo[0]
            longitude = geo[1]
        else:
            geo = (
                loc_dom.xpath("//iframe/@src")[0]
                .split("!2d")[-1]
                .split("!2m")[0]
                .split("!3d")
            )
            latitude = geo[1]
            longitude = geo[0]
        hoo = loc_dom.xpath(
            '//h3[strong[contains(text(), "Our doors")]]/following-sibling::p//text()'
        )
        if len(hoo) > 5:
            hoo = hoo = loc_dom.xpath(
                '//h1[@class="vc_custom_heading"]/following-sibling::div[2]//h3[strong[contains(text(), "Our doors")]]/following-sibling::p//text()'
            )
        hoo = [e.strip() for e in hoo]
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
