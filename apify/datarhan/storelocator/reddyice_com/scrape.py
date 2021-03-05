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
    scraped_items = []

    DOMAIN = "reddyice.com"
    start_url = "https://www.reddyice.com/locations"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36",
    }

    response = session.get(start_url, headers=headers)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//a[@class="base-color-two"]/@href')

    for url in all_locations:
        store_url = urljoin(start_url, url)
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//div[@class="row top"]/h1/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_address = re.findall("contentString = '(.+)';", loc_response.text)[0].split(
            "</br>"
        )
        raw_address = [elem.strip() for elem in raw_address if elem.strip()]
        street_address = raw_address[0]
        city = raw_address[1].split(">")[-1]
        state = raw_address[2].split()[0]
        zip_code = raw_address[2].split()[-1]
        country_code = "<MISSING>"
        store_number = re.findall(r"\d+", store_url)[0]
        store_number = store_number if store_number else "<MISSING>"
        phone = raw_address[-2]
        location_type = "<MISSING>"
        geo = (
            re.findall(r'LatLng\((.+)"\);', loc_response.text)[0]
            .replace('"', "")
            .split(",")
        )
        latitude = geo[0]
        latitude = latitude if latitude else "<MISSING>"
        longitude = geo[1]
        longitude = longitude if longitude else "<MISSING>"
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

        if store_number not in scraped_items:
            scraped_items.append(store_number)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
