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

    items = []

    DOMAIN = "cottman.com"
    start_url = "https://www.cottman.com/location/"

    response = session.get(start_url, verify=False)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//a[contains(@href, "/location/")]/@href')

    for store_url in all_locations:
        if store_url == "https://www.cottman.com/location/":
            continue
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        raw_address = loc_dom.xpath('//meta[@property="og:description"]/@content')[
            -1
        ].split("\n")[2:5]
        raw_address = [elem.strip() for elem in raw_address if elem.strip()]
        if "Main Phone" not in raw_address[-1]:
            raw_address = loc_dom.xpath('//meta[@property="og:description"]/@content')[
                -1
            ].split("\n")[2:6]
            raw_address = [elem.strip() for elem in raw_address if elem.strip()]
            raw_address = [" ".join(raw_address[:2])] + raw_address[2:]
        if "Transmission" in raw_address[0]:
            raw_address = loc_dom.xpath('//meta[@property="og:description"]/@content')[
                -1
            ].split("\n")[3:6]
            raw_address = [elem.strip() for elem in raw_address if elem.strip()]

        location_name = loc_dom.xpath('//meta[@property="og:title"]/@content')[-1]
        street_address = raw_address[0].strip()
        city = raw_address[1].strip().split(", ")[0]
        state = raw_address[1].strip().split(", ")[-1].split()[0]
        zip_code = raw_address[1].strip().split(", ")[-1].split()[-1]
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = raw_address[-1].split(":")[-1].strip()
        location_type = "<MISSING>"
        latitude = re.findall('latitude":"(.+?)"', loc_response.text)[0]
        longitude = re.findall('longitude":"(.+?)"', loc_response.text)[0]
        hours_of_operation = loc_dom.xpath(
            '//h3[strong[contains(text(), "Hours:")]]/following-sibling::p[1]//text()'
        )
        hours_of_operation = [
            elem.strip() for elem in hours_of_operation if elem.strip()
        ]
        hours_of_operation = (
            " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
        )

        if len(city.split()) > 2:
            state = city.split()[-2]
            zip_code = city.split()[-1]
            city = city.split(state)[0]

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
