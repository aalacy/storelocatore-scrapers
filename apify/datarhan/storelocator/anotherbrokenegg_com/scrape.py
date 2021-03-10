import csv
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w") as output_file:
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

    DOMAIN = "anotherbrokenegg.com"
    start_url = "https://anotherbrokenegg.com/list-indexed-business"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//div[@class="field-tile"]/a/@href')
    next_page = dom.xpath('//a[@title="Go to next page"]/@href')
    while next_page:
        response = session.get(urljoin(start_url, next_page[0]))
        dom = etree.HTML(response.text)
        all_locations += dom.xpath('//div[@class="field-tile"]/a/@href')
        next_page = dom.xpath('//a[@title="Go to next page"]/@href')

    for url in all_locations:
        store_url = urljoin(start_url, url)
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//h2[@class="shorter business-name"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        address_raw = loc_dom.xpath(
            '//div[@class="views-field views-field-field-postaladdress-postal-code"]/div/text()'
        )
        street_address = address_raw[0]
        street_address = street_address if street_address else "<MISSING>"
        city = address_raw[1].split(" - ")[0]
        city = city if city else "<MISSING>"
        state = address_raw[1].split(" - ")[1]
        state = state if state else "<MISSING>"
        zip_code = address_raw[1].split(" - ")[2]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = loc_dom.xpath(
            '//div[@class="views-field views-field-field-phone"]/div/a/text()'
        )
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        if "Coming Soon" in location_name:
            location_type = "coming soon"
        geo = (
            loc_dom.xpath('//a[@class="googlepluss"]/@href')[0]
            .split("@")[-1]
            .split(",")[:2]
        )
        if len(geo) == 1:
            geo = loc_dom.xpath(
                '//div[@class="field field-name-field-googletour field-type-link-field field-label-hidden connect-icons-field"]//a/@href'
            )
            geo = geo[0].split("@")[-1].split(",")[:2] if geo else ""
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        if geo:
            latitude = geo[0]
            longitude = geo[1]
        hours_of_operation = loc_dom.xpath('//div[contains(@class,"-time")]//text()')
        hours_of_operation = [
            elem.strip() for elem in hours_of_operation if elem.strip()
        ][1:]
        hours_of_operation = (
            " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
        )
        if location_type == "coming soon":
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
