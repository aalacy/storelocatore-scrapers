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
    session = SgRequests().requests_retry_session(retries=0, backoff_factor=0.3)

    items = []

    DOMAIN = "getairsports.com"
    start_url = "https://getairsports.com/park-locator/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//div[@class="states defaults"]//a/@href')
    all_locations += dom.xpath('//div[@class="statess"]//a/@href')

    for store_url in all_locations:
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        if "getairsports.com" not in store_url:
            continue
        location_name = loc_dom.xpath('//meta[@property="og:site_name"]/@content')
        location_name = location_name[0] if location_name else "<MISSING>"
        address_raw = loc_dom.xpath('//a[@class="local-address"]/text()')[0].split(", ")
        if len(address_raw) > 3:
            address_raw = [", ".join(address_raw[:2])] + address_raw[2:]
        street_address = address_raw[0]
        city = address_raw[1]
        state = address_raw[2].split()[0]
        if len(state) > 2:
            continue
        zip_code = " ".join(address_raw[2].split()[1:])
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = loc_dom.xpath('//a[@class="local-number"]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = "<MISSING>"

        item = [
            DOMAIN,
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
