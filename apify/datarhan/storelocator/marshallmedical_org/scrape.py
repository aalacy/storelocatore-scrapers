import csv
from lxml import etree
from urllib.parse import urljoin

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

    DOMAIN = "marshallmedical.org"
    start_url = "https://www.marshallmedical.org/locations/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath("//li[@data-title]")
    for poi in all_locations:
        url = poi.xpath(".//a/@href")[0]
        store_url = urljoin(start_url, url)
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath(
            '//div[@itemscope]/meta[@itemprop="name"]/@content'
        )
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = loc_dom.xpath(
            '//div[@itemscope]/meta[@itemprop="streetAddress"]/@content'
        )
        street_address = street_address[0] if street_address else "<MISSING>"
        city = loc_dom.xpath(
            '//div[@itemscope]/meta[@itemprop="addressLocality"]/@content'
        )
        city = city[0] if city else "<MISSING>"
        state = loc_dom.xpath(
            '//div[@itemscope]/meta[@itemprop="addressRegion"]/@content'
        )
        state = state[0] if state else "<MISSING>"
        zip_code = loc_dom.xpath(
            '//div[@itemscope]/meta[@itemprop="postalCode"]/@content'
        )
        zip_code = zip_code[0] if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = loc_dom.xpath('//div[@itemscope]/meta[@itemprop="telephone"]/@content')
        phone = phone[0] if phone else "<MISSING>"
        location_type = loc_dom.xpath(
            '//div[@class="all-the-schema" and @itemscope]/@itemtype'
        )
        location_type = (
            location_type[0].split("/")[-1] if location_type else "<MISSING>"
        )
        latitude = poi.xpath("@data-latitude")
        latitude = latitude[0] if latitude else "<MISSING>"
        longitude = poi.xpath("@data-longitude")
        longitude = longitude[0] if longitude else "<MISSING>"
        hours_of_operation = loc_dom.xpath(
            '//strong[contains(text(), "Hours")]/following-sibling::ul/li//text()'
        )
        hours_of_operation = [
            elem.strip() for elem in hours_of_operation if elem.strip()
        ]
        hours_of_operation = (
            " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
        )

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
