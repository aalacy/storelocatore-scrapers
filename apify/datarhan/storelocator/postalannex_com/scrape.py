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

    DOMAIN = "postalannex.com"

    start_url = "https://www.postalannex.com/locations"
    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_poi_html = dom.xpath('//div[@id="filtered-locations"]')
    for poi_html in all_poi_html:
        store_url = "https://www.postalannex.com" + poi_html.xpath(".//a/@href")[0]
        location_name = poi_html.xpath('.//div[@class="storename"]/a/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = poi_html.xpath('.//div[@class="loc-sub"]/a/text()')
        street_address = street_address[0] if street_address else "<MISSING>"
        city = poi_html.xpath('.//div[@class="loc-sub"]/text()')[0].split(",")
        city = city[0] if city else "<MISSING>"
        state = (
            poi_html.xpath('.//div[@class="loc-sub"]/text()')[0]
            .split(",")[-1]
            .strip()
            .split()
        )
        state = state[0] if state else "<MISSING>"
        zip_code = poi_html.xpath('.//div[@class="loc-sub"]/text()')
        zip_code = (
            zip_code[0].split(",")[-1].strip().split()[-1] if zip_code else "<MISSING>"
        )
        country_code = ""
        country_code = country_code if country_code else "<MISSING>"
        store_number = store_url.split("/")[-1]
        store_number = store_number if store_number else "<MISSING>"
        phone = poi_html.xpath('.//a[contains(@href, "tel")]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = ""
        location_type = location_type if location_type else "<MISSING>"

        poi_response = session.get(store_url)
        poi_dom = etree.HTML(poi_response.text)
        street_address_raw = poi_dom.xpath(
            '//div[@itemscope="itemscope"]/div/span[@itemprop="streetAddress"]/text()'
        )
        if len(street_address_raw) == 3:
            street_address += ", " + street_address_raw[-1]
        latitude = poi_dom.xpath('//meta[@name="geo.position"]/@content')
        latitude = latitude[0].split(";")[0] if latitude else "<MISSING>"
        longitude = poi_dom.xpath('//meta[@name="geo.position"]/@content')
        longitude = longitude[0].split(";")[-1] if longitude else "<MISSING>"
        hours_of_operation = poi_dom.xpath(
            '//div[contains(@class, "store-hours")]//text()'
        )
        hours_of_operation = [
            elem.strip() for elem in hours_of_operation if elem.strip()
        ][1:]
        hours_of_operation = (
            ", ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
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

        if store_number not in scraped_items:
            scraped_items.append(store_number)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
