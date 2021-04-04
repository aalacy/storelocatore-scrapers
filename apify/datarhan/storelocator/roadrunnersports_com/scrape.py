import re
import csv
import json
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

    DOMAIN = "roadrunnersports.com"
    start_urls = [
        "https://stores.roadrunnersports.com/ca/",
        "https://stores.roadrunnersports.com/wa/",
        "https://stores.roadrunnersports.com/or/",
        "https://stores.roadrunnersports.com/az/",
        "https://stores.roadrunnersports.com/co/",
        "https://stores.roadrunnersports.com/il/",
        "https://stores.roadrunnersports.com/oh/",
        "https://stores.roadrunnersports.com/ga/",
        "https://stores.roadrunnersports.com/va/",
        "https://stores.roadrunnersports.com/md/",
        "https://stores.roadrunnersports.com/pa/",
        "https://stores.roadrunnersports.com/nj/",
    ]

    all_locations = []
    for url in start_urls:
        response = session.get(url)
        dom = etree.HTML(response.text)
        all_locations += dom.xpath('//div[@class="map-list-item is-single"]/a/@href')

    for store_url in all_locations:
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        raw_address = loc_dom.xpath(
            '//div[@class="col-8 map-list-item-address mt-10 mb-10"]/span/text()'
        )

        store_url = loc_dom.xpath(
            '//div[@class="col map-list-item-info mt-10 mb-10"]/a/@href'
        )[0]
        location_name = loc_dom.xpath(
            '//h2[@class="map-list-item-name-secondary text-uppercase"]/text()'
        )
        location_name = [elem.strip() for elem in location_name]
        location_name = " ".join(location_name)
        street_address = raw_address[0]
        city = raw_address[-1].split(", ")[0]
        state = raw_address[-1].split(", ")[-1].split()[0]
        zip_code = raw_address[-1].split(", ")[-1].split()[-1]
        country_code = "<MISSING>"
        store_number = loc_dom.xpath("//@data-fid")
        store_number = store_number[0] if store_number else "<MISSING>"
        phone = loc_dom.xpath('//a[@alt="Call Store"]/strong/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = re.findall(r'lat":(.+?),', loc_response.text)[0]
        longitude = re.findall(r'lng":(.+?),', loc_response.text)[0]
        hours_of_operation = []
        hoo = loc_dom.xpath('//script[contains(text(), "primary =")]/text()')[0]
        hoo = re.findall("primary = (.+?);", hoo)[0]
        hoo = json.loads(hoo)
        for day, hours in hoo["days"].items():
            if hours != "closed":
                opens = hours[0]["open"]
                closes = hours[0]["close"]
                hours_of_operation.append(f"{day} {opens} - {closes}")
            else:
                hours_of_operation.append(f"{day} closed")
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
