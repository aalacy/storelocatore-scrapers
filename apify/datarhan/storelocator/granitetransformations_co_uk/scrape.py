import csv
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl


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

    DOMAIN = "granitetransformations.co.uk"
    start_url = "https://www.granitetransformations.co.uk/locations/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//span[@class="name"]/a/@href')
    for store_url in all_locations:
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        raw_address = loc_dom.xpath(
            '//a[@class="franchise_tile col-md-4"]/span[@class="excerpt"]/text()'
        )[0].strip()
        addr = parse_address_intl(raw_address)
        location_name = loc_dom.xpath('//strong[@class="brand"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address = "{} {}".format(
                addr.street_address_2, addr.street_address_1
            )
        location_type = "<MISSING>"
        city = addr.city
        city = city if city else "<MISSING>"
        state = addr.state
        state = state if state else "<MISSING>"
        zip_code = addr.postcode
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = addr.country
        country_code = country_code if country_code else "<MISSING>"
        store_number = "<MISSING>"
        phone = loc_dom.xpath('//a[contains(@href, "tel")]/span/text()')
        phone = phone[0] if phone else "<MISSING>"
        geo = (
            loc_dom.xpath('//img[contains(@data-src, "map")]/@data-src')[0]
            .split("map-")[-1]
            .split("-")[:3]
        )
        if geo[-1] == "385":
            geo = geo[:-1]
        latitude = geo[0]
        latitude = latitude if latitude else "<MISSING>"
        longitude = geo[-1]
        longitude = longitude if longitude else "<MISSING>"
        hoo = loc_dom.xpath('//div[@class="franchise_tile col-md-4"]//table//text()')
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
