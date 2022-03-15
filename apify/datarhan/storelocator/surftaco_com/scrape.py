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

    start_url = "https://surftaco.com/locations/"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="location_title"]/a/@href')
    for store_url in all_locations:
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//h1[@class="entry-title"]/text()')
        location_name = location_name[0].strip() if location_name else "<MISSING>"
        raw_address = loc_dom.xpath('//div[@class="street_address"]/text()')[0].split(
            ", "
        )
        street_address = raw_address[0]
        city = raw_address[1]
        zip_code = "<MISSING>"
        state = raw_address[-1]
        if len(state.split()) == 2:
            zip_code = state.split()[-1]
            state = state.split()[0]
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = loc_dom.xpath('//div[@class="location_address"]/p/text()')
        phone = phone[-1].strip() if phone else "<MISSING>"
        if phone == "<MISSING>":
            phone = loc_dom.xpath('//div[@class="street_address"]/text()')[-1]
        if "4050 U" in phone:
            phone = loc_dom.xpath('//div[@class="location_address"]/div/text()')[-1]
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hoo = loc_dom.xpath('//div[@class="location_address"]/p/text()')[:-1]
        hoo = [e.strip() for e in hoo if e.strip()]
        if not hoo:
            hoo = loc_dom.xpath('//div[@class="location_address"]/div[2]/text()')
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
