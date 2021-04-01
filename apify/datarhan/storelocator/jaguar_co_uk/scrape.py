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
    scraped_items = []

    DOMAIN = "jaguar.co.uk"
    start_url = "https://www.jaguar.co.uk/retailers/retailer-opening-information.html"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36"
    }

    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//th[@class="tg-yseo"]/a/@href')
    for store_url in all_locations:
        loc_response = session.get(store_url, headers=hdr)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath(
            '//h1[contains(@class, "headerBox__heroTitle")]/text()'
        )
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = loc_dom.xpath(
            '//span[@class="retailerContact__address1"]/text()'
        )[0]
        street_2 = loc_dom.xpath('//span[@class="retailerContact__address2"]/text()')
        if street_2:
            street_address += " " + street_2[0]
        street_3 = loc_dom.xpath('//span[@class="retailerContact__address3"]/text()')
        if street_3:
            street_address += " " + street_3[0]
        city = loc_dom.xpath('//span[@class="retailerContact__locality"]/text()')
        city = city[0] if city else "<MISSING>"
        state = loc_dom.xpath('//span[@class="retailerContact__county"]/text()')
        state = state[0] if state else "<MISSING>"
        zip_code = loc_dom.xpath('//span[@class="retailerContact__postcode"]/text()')
        zip_code = zip_code[0] if zip_code else "<MISSING>"
        country_code = "UK"
        store_number = "<MISSING>"
        phone = loc_dom.xpath('//a[@class="tel"]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = loc_dom.xpath("//@data-lat")
        latitude = latitude[0] if latitude else "<MISSING>"
        longitude = loc_dom.xpath("//@data-long")
        longitude = longitude[0] if longitude else "<MISSING>"
        hoo = loc_dom.xpath(
            '//h2[contains(text(), "SALES OPENING TIMES")]/following-sibling::table//text()'
        )
        hoo = [e.strip() for e in hoo if e.strip()]
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
        check = f"{location_name} {street_address}"
        if check not in scraped_items:
            scraped_items.append(check)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
