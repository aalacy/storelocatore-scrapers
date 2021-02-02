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

    DOMAIN = "thedaileymethod.com"
    start_url = "https://thedaileymethod.com/studios/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//ul[@class="city-list clean inline pack"]//a/@href')

    for store_url in all_locations:
        loc_response = session.get(store_url + "contact/")
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//span[@class="location-title"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        if "Mexico" in location_name:
            continue
        street_address = loc_dom.xpath('//div[@class="address"]/text()')
        if "any questions" in street_address[0]:
            street_address = street_address[1:]
        street_address = street_address[0] if street_address else "<MISSING>"
        city = loc_dom.xpath('//span[@class="city"]/text()')
        city = city[0] if city else "<MISSING>"
        state = loc_dom.xpath('//span[@class="state"]/text()')
        state = state[0].split()[-1] if state else "<MISSING>"
        zip_code = loc_dom.xpath('//span[@class="zip"]/text()')
        zip_code = zip_code[0].replace("C.P.", "") if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = loc_dom.xpath('//div[@class="phone"]/text()')
        phone = phone[0].split(": ")[-1] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = loc_dom.xpath("//@data-lat")[0]
        longitude = loc_dom.xpath("//@data-lng")[0]
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
