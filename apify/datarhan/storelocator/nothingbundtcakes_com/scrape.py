import re
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

    DOMAIN = "nothingbundtcakes.com"

    items = []
    gathered_items = []

    start_url = "https://www.nothingbundtcakes.com/bakeries?"
    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_poi_html = dom.xpath(
        '//div[@class="search-results"]/div[@class="bakeries"]/div'
    )
    next_page = (
        "https://www.nothingbundtcakes.com"
        + dom.xpath('//span[@class="next control"]/a/@href')[0]
    )
    while next_page:
        next_response = session.get(next_page)
        page_dom = etree.HTML(next_response.text)
        page_poi_html = page_dom.xpath(
            '//div[@class="search-results"]/div[@class="bakeries"]/div'
        )
        all_poi_html += page_poi_html
        next_page = page_dom.xpath('//span[@class="next control"]/a/@href')
        if next_page:
            next_page = "https://www.nothingbundtcakes.com" + next_page[0]

    for poi_html in all_poi_html:
        store_url = poi_html.xpath('.//a[@class="btn visit-bakery-page"]/@href')
        store_url = (
            "https://www.nothingbundtcakes.com/" + store_url[0]
            if store_url
            else "<MISSING>"
        )
        location_name = poi_html.xpath('.//div[@class="name"]/div/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        if "Coming Soon" in location_name:
            continue
        street_address = poi_html.xpath('.//p[@class="line1 line"]/text()')
        street_address = street_address[0] if street_address else "<MISSING>"
        street_address_2 = poi_html.xpath('.//p[@class="line2 line"]/text()')
        if street_address_2:
            street_address += " " + street_address_2[0]
        city = poi_html.xpath('.//span[@class="city"]/text()')
        city = city[0] if city else "<MISSING>"
        state = poi_html.xpath('.//span[@class="state"]/text()')
        state = state[0] if state else "<MISSING>"
        zip_code = poi_html.xpath('.//span[@class="postal_code"]/text()')
        zip_code = zip_code[0] if zip_code else "<MISSING>"
        country_code = ""
        country_code = country_code if country_code else "<MISSING>"
        store_number = ""
        store_number = store_number if store_number else "<MISSING>"
        phone = poi_html.xpath('.//p[@class="phone"]/a/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        geo_data = poi_html.xpath('.//a[contains(@href, "maps")]/@href')
        geo_data = geo_data[0] if geo_data else "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        if geo_data == "<MISSING>":
            latitude = re.findall(r"/@(.+)/data", geo_data)
            latitude = latitude[0].split(",")[0] if latitude else "<MISSING>"
            longitude = re.findall(r"/@(.+)/data", geo_data)
            longitude = longitude[0].split(",")[0] if longitude else "<MISSING>"
        hours_of_operation = poi_html.xpath('//div[@class="hours"]//text()')
        hours_of_operation = [
            elem.strip() for elem in hours_of_operation if elem.strip()
        ]
        hours_of_operation = (
            " ".join(hours_of_operation[1:]).split("*")[0].strip()
            if hours_of_operation
            else "<MISSING>"
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

        check = location_name.strip().lower() + " " + street_address.strip().lower()
        if check not in gathered_items:
            gathered_items.append(check)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
