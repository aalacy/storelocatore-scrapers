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

    start_url = "https://www.kowalskis.com/find-store"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//a[contains(text(), "Store Details")]/@href')
    for store_url in all_locations:
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath("//h1/span/text()")[0]
        street_address = loc_dom.xpath('//span[@class="address-line1"]/text()')[0]
        city = loc_dom.xpath('//span[@class="locality"]/text()')[0]
        state = loc_dom.xpath('//span[@class="administrative-area"]/text()')[0]
        zip_code = loc_dom.xpath('//span[@class="postal-code"]/text()')[0]
        country_code = loc_dom.xpath('//span[@class="country"]/text()')[0]
        store_number = "<MISSING>"
        phone = loc_dom.xpath('//div[@class="field phone label-inline"]//a/text()')[0]
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hoo = loc_dom.xpath(
            '//p[strong[contains(text(), "Grocery Store Hours")]]/text()'
        )
        hoo = [e.strip() for e in hoo if e.strip() and "a.m" in e]
        if not hoo:
            hoo = loc_dom.xpath(
                '//div[contains(text(), "Store Hours")]/following-sibling::div[1]//text()'
            )
        hoo = [e.strip() for e in hoo if e.strip() and "a.m" in e]
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
