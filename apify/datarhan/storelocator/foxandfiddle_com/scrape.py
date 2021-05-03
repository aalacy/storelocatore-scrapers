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

    start_url = "https://foxandfiddle.com/locations"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[contains(@class, "location__gps")]/@data-href')
    for store_url in all_locations:
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath("//h1//text()")
        location_name = " ".join(location_name) if location_name else "<MISSING>"
        street_address = loc_dom.xpath(
            '//div[@class="location__address text--upper"]/text()'
        )
        street_address = street_address[0].strip() if street_address else "<MISSING>"
        raw_data = (
            loc_dom.xpath('//div[@class="location__city text--transport"]/text()')[0]
            .strip()
            .split(", ")
        )
        city = " ".join(raw_data[0].split()[:-1])
        state = raw_data[0].split()[-1]
        zip_code = raw_data[-1].strip()
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = loc_dom.xpath('//div[@class="location__phone"]/text()')
        phone = phone[-1] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = loc_dom.xpath("//@data-lat")[0]
        longitude = loc_dom.xpath("//@data-lng")[0]
        days = loc_dom.xpath('//ul[@class="days text--upper"]/li/text()')
        hours = loc_dom.xpath(
            '//div[@class="col-md-4 col-xs-6 text--transport"]/li/text()'
        )
        hoo = list(map(lambda d, h: d + " " + h, days, hours))
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
