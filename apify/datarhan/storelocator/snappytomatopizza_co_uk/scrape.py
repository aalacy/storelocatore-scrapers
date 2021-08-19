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
    session = SgRequests()

    items = []

    DOMAIN = "snappytomatopizza.co.uk"
    start_url = "https://snappytomatopizza.co.uk/selector/restaurant/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@id="storeItems"]//@data-url')
    for store_url in all_locations:
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//div[@class="map_store__title"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = loc_dom.xpath('//div[@class="map_store__address"]/text()')[
            0
        ].split()[:-2]
        street_address = " ".join(street_address) if street_address else "<MISSING>"
        city = location_name.split(" - ")[0]
        state = "<MISSING>"
        zip_code = loc_dom.xpath('//div[@class="map_store__address"]/text()')[
            0
        ].split()[-2:]
        zip_code = " ".join(zip_code)
        country_code = "<MISSING>"
        store_number = store_url.split("/")[-2]
        phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')
        phone = phone[0].split(":")[-1].strip() if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = loc_dom.xpath("//@data-latitude")
        latitude = latitude[0] if latitude else "<MISSING>"
        longitude = loc_dom.xpath("//@data-longitude")
        longitude = longitude[0].strip() if longitude else "<MISSING>"
        hoo = []
        hours = loc_dom.xpath(
            '//div[@class="store_schedule desktop_store__bl"]//div[contains(@class, "table_row")]'
        )[1:]
        for elem in hours:
            day = elem.xpath('.//div[@class="table_day"]/span/text()')[0]
            opens = elem.xpath('.//div[@class="table_open"]/span/text()')
            opens = opens[0] if opens else "closed"
            closes = elem.xpath('.//div[@class="table_close"]/span/text()')
            closes = closes[0] if closes else "closed"
            if opens == "closed":
                hoo.append(f"{day} closed")
            else:
                hoo.append(f"{day} {opens} - {closes}")
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

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
