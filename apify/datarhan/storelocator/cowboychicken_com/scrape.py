import csv
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_usa


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

    DOMAIN = "cowboychicken.com"
    start_url = "https://www.cowboychicken.com/locations/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="list-box-con-1"]')
    for poi_html in all_locations:
        store_url = poi_html.xpath('.//div[@class="list-left-con"]/a[1]/@href')
        store_url = urljoin(start_url, store_url[0]) if store_url else "<MISSING>"
        location_name = poi_html.xpath('.//div[@class="list-left-con"]/a[1]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_address = poi_html.xpath('.//p[@class="address-block"]/text()')[0].strip()
        parsed_adr = parse_address_usa(raw_address)
        country_code = parsed_adr.country
        city = parsed_adr.city
        city = city if city else "<MISSING>"
        street_address = parsed_adr.street_address_1
        try:
            if street_address.street_address_2:
                street_address += " " + street_address.street_address_2
        except:
            pass
        state = parsed_adr.state
        zip_code = parsed_adr.postcode
        store_number = "<MISSING>"
        phone = poi_html.xpath('.//a[@class="number-block"]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi_html.xpath(".//preceding-sibling::input[3]/@value")[0]
        longitude = poi_html.xpath(".//preceding-sibling::input[2]/@value")[0]
        hoo = poi_html.xpath('.//ul[@class="inner"]//text()')
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
