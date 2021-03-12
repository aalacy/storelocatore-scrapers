import re
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

    DOMAIN = "homelandstores.com"
    start_url = "https://www.homelandstores.com/StoreLocator/"

    all_locations = []
    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_states = dom.xpath(
        '//h3[contains(text(), "Our stores are in the following states:")]/following-sibling::div//a/@href'
    )
    for url in all_states:
        response = session.get(urljoin(start_url, url))
        dom = etree.HTML(response.text)
        all_locations += dom.xpath('//td[@align="right"]/a/@href')

    for url in all_locations:
        poi_url = urljoin(start_url, url)
        loc_response = session.get(poi_url)
        loc_dom = etree.HTML(loc_response.text)

        poi_name = loc_dom.xpath("//title/text()")[0].split("for ")[-1]
        raw_address = loc_dom.xpath('//p[@class="Address"]/text()')
        raw_address = [elem.strip() for elem in raw_address if elem.strip()]
        street = raw_address[0]
        city = raw_address[-1].split(", ")[0]
        state = raw_address[-1].split(", ")[-1].split()[0]
        zip_code = raw_address[-1].split(", ")[-1].split()[-1]
        country_code = "<MISSING>"
        poi_number = poi_name.split()[-1]
        poi_number = poi_number if poi_number else "<MISSING>"
        phone = loc_dom.xpath('//p[@class="PhoneNumber"]/a/text()')
        phone = phone[0] if phone else "<MISSING>"
        poi_type = "<MISSING>"
        geo = re.findall(
            r'initializeMap\("(.+?)"\);', loc_response.text.replace("\n", "")
        )[0].split('","')
        latitude = geo[0]
        latitude = "<MISSING>" if latitude == "" else latitude
        longitude = geo[1]
        longitude = "<MISSING>" if longitude == "" else longitude
        hoo = loc_dom.xpath(
            '//dt[contains(text(), "Pharmacy Hours:")]/following-sibling::dd[1]//text()'
        )
        hoo = [elem.strip() for elem in hoo]
        if not hoo:
            hoo = loc_dom.xpath(
                '//dt[contains(text(), "Hours of Operation:")]/following-sibling::dd/text()'
            )
        hoo = " ".join(hoo) if hoo else "<MISSING>"

        item = [
            DOMAIN,
            poi_url,
            poi_name,
            street,
            city,
            state,
            zip_code,
            country_code,
            poi_number,
            phone,
            poi_type,
            latitude,
            longitude,
            hoo,
        ]

        items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
