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

    start_url = "https://tommyjohn.com/pages/store-directory"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[contains(@class, "stores-section city")]')
    for poi_html in all_locations:
        store_url = start_url
        location_name = poi_html.xpath('.//h2[@class="stores-section__heading"]/text()')
        location_name = location_name[0].strip() if location_name else "<MISSING>"
        raw_address = poi_html.xpath(
            './/div[@class="stores-section__text-container-sub"]/p[1]/text()'
        )
        raw_address = [
            " ".join([i for i in e.split() if i.strip()])
            for e in raw_address
            if e.strip()
        ]
        location_type = "<MISSING>"
        if "#ComfortSoon!" in raw_address[0]:
            location_type = "coming soon"
            raw_address = raw_address[1:]
        street_address = raw_address[0]
        city = poi_html.xpath(
            './/p[@class="stores-section__content-section stores-section__content-city"]/text()'
        )
        city = city[0] if city else "<MISSING>"
        state = raw_address[1].split(",")[1].strip()
        zip_code = raw_address[1].split(",")[-1].strip()
        country_code = "United States"
        store_number = "<MISSING>"
        phone = poi_html.xpath(
            './/p[@class="stores-section__content-section stores-section__content-phone"]/a/text()'
        )
        phone = phone[0] if phone else "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hoo = poi_html.xpath(
            './/p[@class="stores-section__content-section stores-section__content-hours"]//text()'
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
