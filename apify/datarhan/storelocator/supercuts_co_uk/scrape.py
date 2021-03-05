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

    DOMAIN = "supercuts.co.uk"
    start_url = "https://www.supercuts.co.uk/salon-locator/?show-all=yes"

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//div[@class="list-salons"]//li/a[contains(@href, "/salon/")]/@href'
    )
    for store_url in all_locations:
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//div[@class="salon-single-left"]/h3/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_address = loc_dom.xpath('//p[@class="address"]/text()')
        if not raw_address:
            continue
        if len(raw_address) == 5:
            raw_address = [" ".join(raw_address[:2])] + raw_address[2:]
        street_address = raw_address[0]
        if len(raw_address) == 4:
            city = raw_address[1].strip()
            state = raw_address[2].strip()
            zip_code = raw_address[3].strip()
        else:
            city = raw_address[1].strip()
            state = "<MISSING>"
            zip_code = raw_address[-1].strip()
        if "/" in city:
            street_address += " " + city
            city = state
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        phone = loc_dom.xpath(
            '//p[@class="phone"]/a[@class="phone-tracked-link"]/text()'
        )
        phone = phone[0].strip() if phone and phone[0].strip() else "<MISSING>"
        latitude = loc_dom.xpath("//@data-lat")
        latitude = latitude[0] if latitude else "<MISSING>"
        longitude = loc_dom.xpath("//@data-lng")
        longitude = longitude[0] if longitude else "<MISSING>"
        hoo = loc_dom.xpath(
            '//h5[contains(text(), "Opening Hours")]/following-sibling::div[1]//text()'
        )
        hoo = [elem.strip() for elem in hoo if elem.strip()]
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
