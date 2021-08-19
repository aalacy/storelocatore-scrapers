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

    DOMAIN = "crye-leike.com"
    start_url = "https://www.crye-leike.com/real-estate-offices"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath("//div[@itemscope]")
    next_page = dom.xpath('//a[contains(text(), "Next")]/@href')
    while next_page:
        response = session.get(next_page[0])
        dom = etree.HTML(response.text)
        all_locations += dom.xpath("//div[@itemscope]")
        next_page = dom.xpath('//a[contains(text(), "Next")]/@href')
        if "javascript:void" in next_page[0]:
            next_page = ""

    for poi_html in all_locations:
        store_url = poi_html.xpath(
            './/div[@class="btnwrap"]/a[i[@class="fa fa-building"]]/@href'
        )
        if not store_url:
            continue
        store_url = store_url[0] if store_url else "<MISSING>"
        location_name = poi_html.xpath('.//span[@itemprop="name"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = poi_html.xpath('.//span[@itemprop="streetAddress"]/text()')
        street_address = street_address[0] if street_address else "<MISSING>"
        city = poi_html.xpath('.//span[@itemprop="addressLocality"]/text()')
        city = city[0].replace(",", "") if city else "<MISSING>"
        state = poi_html.xpath('.//span[@itemprop="addressRegion"]/text()')
        state = state[0] if state else "<MISSING>"
        zip_code = poi_html.xpath('.//span[@itemprop="postalCode"]/text()')
        zip_code = zip_code[0] if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = poi_html.xpath('.//span[@itemprop="telephone"]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi_html.xpath('.//meta[@itemprop="latitude"]/@content')
        latitude = latitude[0] if latitude and latitude[0].strip() else "<MISSING>"
        longitude = poi_html.xpath('.//meta[@itemprop="longitude"]/@content')
        longitude = longitude[0] if longitude and longitude[0].strip() else "<MISSING>"
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
