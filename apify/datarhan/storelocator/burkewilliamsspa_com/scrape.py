import re
import csv
from lxml import etree
from urllib.parse import urljoin

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

    start_url = "https://www.burkewilliams.com/"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//a[contains(text(), "LOCATIONS")]/following-sibling::ul//a/@href'
    )
    for url in all_locations:
        store_url = urljoin(start_url, url)
        loc_reposne = session.get(store_url)
        loc_dom = etree.HTML(loc_reposne.text)

        location_name = loc_dom.xpath("//h1/text()")
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_data = loc_dom.xpath('//p[strong[contains(text(), "Address")]]/text()')
        if not raw_data:
            raw_data = loc_dom.xpath(
                '//div[span[strong[contains(text(), "Address")]]]/text()'
            )
        street_address = raw_data[0]
        city = raw_data[1].split(", ")[0]
        state = raw_data[1].split(", ")[-1].split()[0]
        zip_code = raw_data[1].split(", ")[-1].split()[-1]
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = loc_dom.xpath('//p[strong[contains(text(), "Address")]]/text()')
        phone = [e.strip() for e in phone if "Phone" in e]
        phone = phone[0].split(":")[-1].strip() if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hoo = loc_dom.xpath(
            '//p[strong[contains(text(), "Hours of Operation")]]/text()'
        )
        if not hoo:
            hoo = loc_dom.xpath('//div[span[strong[contains(text(), "Hours")]]]/text()')
        if not hoo:
            hoo = loc_dom.xpath('//p[contains(text(), "Thursday")]/text()')
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = (
            " ".join(hoo).split("First")[0].strip() if hoo else "<MISSING>"
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
