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
    session = SgRequests().requests_retry_session(retries=0, backoff_factor=0.3)

    items = []

    DOMAIN = "firstbankonline.com"
    start_url = "https://www.firstbankonline.com/location/?type=branches"
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36"
    }

    response = session.get(start_url, headers=headers)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//a[@class="btn info"]/@href')

    for store_url in all_locations:
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//h2[@class="lightblue h3"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        address_raw = loc_dom.xpath('//p[@class="address"]/text()')
        address_raw = [elem.strip() for elem in address_raw if elem.strip()]
        if len(address_raw) == 3:
            address_raw = [", ".join(address_raw[:2])] + [
                address_raw[2].replace("Franklin\t", "Franklin, ")
            ]
        street_address = address_raw[0]
        street_address = street_address if street_address else "<MISSING>"
        if street_address.endswith(","):
            street_address = street_address[:-1]
        city = address_raw[1].split(", ")[0]
        city = city if city else "<MISSING>"
        state = address_raw[1].split(", ")[-1].split()[0]
        state = state if state else "<MISSING>"
        zip_code = address_raw[1].split(", ")[-1].split()[-1]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = loc_dom.xpath('//a[@class="h5 blue"]/@href')[0].split("//")[-1]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        geo = re.findall(r"LatLng\((.+?)\);", loc_response.text)[-1].split(",")
        latitude = geo[0]
        longitude = geo[1]
        hoo = loc_dom.xpath('//div[@class="hrs"]//text()')
        hoo = [elem.strip() for elem in hoo if elem.strip()]
        if not hoo:
            hoo = loc_dom.xpath('//div[@class="col hours"]/p//text()')[:6]
        hours_of_operation = " ".join(hoo[1:]) if hoo else "<MISSING>"

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
