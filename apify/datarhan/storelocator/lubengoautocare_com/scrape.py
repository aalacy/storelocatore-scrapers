import re
import csv
from lxml import etree
from urllib.parse import urljoin

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

    start_url = "https://lubengoautocare.com/locations-region/"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="the_list_item_action"]/a/@href')[1:]
    for url in all_locations:
        store_url = urljoin(start_url, url)
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        raw_address = loc_dom.xpath(
            '//h3[@class="the_list_item_headline hds_color"]/text()'
        )[0]
        addr = parse_address_intl(raw_address)
        location_name = (
            loc_dom.xpath('//meta[@property="og:title"]/@content')[0]
            .split("|")[0]
            .strip()
        )
        city = addr.city
        street_address = raw_address.split(city)[0].strip()
        if street_address.endswith(","):
            street_address = street_address[:-1]
        state = addr.state
        zip_code = addr.postcode
        country_code = addr.country
        country_code = country_code if country_code else "<MISSING>"
        store_number = "<MISSING>"
        phone = (
            loc_dom.xpath('//h3[contains(text(), "Phone Number:")]/text()')[0]
            .split(":")[-1]
            .strip()
        )
        location_type = "<MISSING>"
        geo = (
            loc_dom.xpath("//iframe/@src")[0]
            .split("!2d")[-1]
            .split("!2")[0]
            .split("!3d")
        )
        latitude = geo[-1].split("!")[0]
        longitude = geo[0]
        hoo = loc_dom.xpath('//p[b[contains(text(), "Hours")]]/text()')
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = (
            "Monday " + " ".join(hoo).split("Monday ")[-1] if hoo else "<MISSING>"
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
