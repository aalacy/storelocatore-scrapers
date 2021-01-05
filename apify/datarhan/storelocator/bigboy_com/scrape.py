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

    DOMAIN = "bigboy.com"
    start_url = "https://www.bigboy.com/big-boy-restaurant-locations/"

    response = session.post(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//a[contains(text(), "location details")]/@href')

    for url in all_locations:
        store_url = urljoin(start_url, url)
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//div[@class="et_pb_text_inner"]/h1/text()')
        location_name = " ".join(location_name) if location_name else "<MISSING>"
        raw_data = loc_dom.xpath('//div[@class="et_pb_blurb_description"]/text()')
        if len(raw_data) == 1:
            raw_data_new = loc_dom.xpath(
                '//div[@class="et_pb_blurb_description"]/p/text()'
            )
            raw_data = raw_data_new[:-1] + raw_data + [raw_data_new[-1]]
        if not raw_data:
            raw_data = loc_dom.xpath('//div[@class="et_pb_blurb_description"]/p/text()')
        if len(raw_data) == 2:
            raw_data = loc_dom.xpath('//div[@class="et_pb_blurb_description"]/p/text()')
            raw_data += loc_dom.xpath('//div[@class="et_pb_blurb_description"]/text()')
        raw_data = [
            elem.strip() for elem in raw_data if elem.strip() and elem.strip() != "@"
        ]
        street_address = raw_data[1]
        city = raw_data[2].split(", ")[0]
        state = raw_data[2].split(", ")[-1].split()[0]
        zip_code = raw_data[2].split(", ")[-1].split()[-1]
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = loc_dom.xpath(
            '//h4[span[contains(text(), "phone")]]/following-sibling::div/text()'
        )
        if not phone:
            phone = loc_dom.xpath(
                '//h4[span[contains(text(), "phone")]]/following-sibling::div/p/text()'
            )
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        geo = re.findall(r"center: \[(.+?)\]", loc_response.text)[0].split(",")
        latitude = geo[0]
        latitude = latitude if latitude else "<MISSING>"
        longitude = geo[-1]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = loc_dom.xpath(
            '//h4[span[contains(text(), "hours")]]/following-sibling::div[1]//text()'
        )
        if not hours_of_operation:
            hours_of_operation = loc_dom.xpath(
                '//h4[span[contains(text(), "hours")]]/following-sibling::div/p/text()'
            )
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
