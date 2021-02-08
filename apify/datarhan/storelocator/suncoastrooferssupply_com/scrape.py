import csv
from urllib.parse import urljoin
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

    DOMAIN = "suncoastrooferssupply.com"
    start_url = "https://suncoastrooferssupply.com/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//a[@title="More Branch Information"]/@href')
    for url in all_locations:
        store_url = urljoin(start_url, url)
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath(
            '//span[@id="ContentPlaceHolder1_BranchName"]/text()'
        )
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = loc_dom.xpath(
            '//span[@id="ContentPlaceHolder1_StreetAddr"]/text()'
        )
        street_address = street_address[0] if street_address else "<MISSING>"
        city = loc_dom.xpath('//span[@id="ContentPlaceHolder1_City"]/text()')
        city = city[0] if city else "<MISSING>"
        state = loc_dom.xpath('//span[@id="ContentPlaceHolder1_StateCd"]/text()')
        state = state[0] if state else "<MISSING>"
        zip_code = loc_dom.xpath('//span[@id="ContentPlaceHolder1_ZipCd"]/text()')
        zip_code = zip_code[0] if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = loc_response.url.split("=")[1].split("&")[0]
        store_number = store_number if store_number else "<MISSING>"
        phone = loc_dom.xpath('//span[@id="ContentPlaceHolder1_Phone2"]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        geo = (
            loc_dom.xpath('//a[@id="ContentPlaceHolder1_hlMap"]/@href')[0]
            .split("=")[-1]
            .split(", ")
        )
        latitude = geo[0]
        longitude = geo[1]
        hours_of_operation = loc_dom.xpath(
            '//span[@id="ContentPlaceHolder1_BusinessHours"]/text()'
        )
        hours_of_operation = (
            hours_of_operation[0] if hours_of_operation else "<MISSING>"
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
