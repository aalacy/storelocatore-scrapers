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

    DOMAIN = "lafamiliapawn.com"
    start_url = "https://www.lafamiliapawn.com/locations/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//a[contains(text(), "Select")]/@href')
    for url in all_locations:
        store_url = urljoin(start_url, url)
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//span[@class="fileTrailCurrent"]/text()')[
            0
        ].split(",")[0]
        raw_address = loc_dom.xpath(
            '//div[@class="col-10 border-lg-top border-black py-3 px-lg-0"]/p/text()'
        )
        raw_address = [e.strip() for e in raw_address]
        street_address = raw_address[0]
        city = raw_address[-1].split(", ")[0]
        state = raw_address[-1].split(", ")[-1].split()[0]
        zip_code = raw_address[-1].split(", ")[-1].split()[-1]
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        geo = (
            loc_dom.xpath('//a[contains(@href, "maps")]/@href')[0]
            .split("/")[-1]
            .split(",")
        )
        latitude = geo[0]
        latitude = latitude if latitude else "<MISSING>"
        longitude = geo[1]
        longitude = longitude if longitude else "<MISSING>"
        hoo = loc_dom.xpath('//ul[@class="list-unstyled"]/li/text()')
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
