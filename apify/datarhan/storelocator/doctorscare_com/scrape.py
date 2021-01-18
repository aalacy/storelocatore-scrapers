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

    DOMAIN = "doctorscare.com"
    start_url = "https://doctorscare.com/locate/"

    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36",
    }
    response = session.get(start_url, headers=headers)
    urls = re.findall("window.location='(.+?)'", response.text)
    urls = [url for url in urls if "http" not in url]

    for url in urls:
        store_url = urljoin(start_url, url)
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//div[@class="loc-header-title"]/text()')
        location_name = location_name[0].strip() if location_name else "<MISSING>"
        address_raw = loc_dom.xpath('//div[@id="locinfodiv"]//text()')
        address_raw = [elem.strip() for elem in address_raw if elem.strip()]
        street_address = address_raw[0]
        street_address = street_address if street_address else "<MISSING>"
        city = address_raw[1].split(", ")[0]
        city = city if city else "<MISSING>"
        state = address_raw[1].split(", ")[-1].split()[0]
        state = state if state else "<MISSING>"
        zip_code = address_raw[1].split(", ")[-1].split()[-1]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = loc_dom.xpath('//strong[contains(text(), "Phone:")]/following::text()')[
            0
        ].strip()
        location_type = "<MISSING>"
        if loc_dom.xpath('//div[contains(text(), "Temporarily Closed")]'):
            location_type = "Temporarily Closed"
        location_type = location_type if location_type else "<MISSING>"
        geo = re.findall(
            "keyword:'{}', (.+?), locstatus".format(url[1:]), loc_response.text
        )[0]
        latitude = re.findall("lat:'(.+?)'", geo)[0]
        longitude = re.findall("lng:'(.+?)'", geo)[0]
        hours_of_operation = loc_dom.xpath(
            '//div[strong[contains(text(), "Mon - Fri:")]]//text()'
        )
        hours_of_operation = [
            elem.strip() for elem in hours_of_operation if elem.strip()
        ]
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
