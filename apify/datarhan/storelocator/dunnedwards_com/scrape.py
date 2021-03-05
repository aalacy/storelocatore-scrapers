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

    DOMAIN = "dunnedwards.com"
    start_url = "https://www.dunnedwards.com/directory/store-list"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//a[contains(text(), "View Details")]/@href')
    for url in all_locations:
        store_url = urljoin(start_url, url)
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//div[@class="page-header-content"]/h1/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        address_raw = loc_dom.xpath('//div[h2[contains(text(), "Store:")]]/text()')
        address_raw = [elem.strip() for elem in address_raw if elem.strip()]
        address_raw = ", ".join(address_raw).replace(" (, )", "")
        street_address = address_raw.split(", ")[0]
        city = address_raw.split(", ")[1]
        state = address_raw.split(", ")[-1].split()[0]
        zip_code = address_raw.split(", ")[-1].split()[-1]
        country_code = "<MISSING>"
        store_number = loc_dom.xpath('//h2[contains(text(), "Store:")]/text()')[
            0
        ].split("-")[-1]
        phone = loc_dom.xpath('//a[@class="phone-number"]/text()')[0]
        location_type = "<MISSING>"
        latitude = (
            loc_dom.xpath('//a[contains(@href, "maps")]/@href')[0]
            .split("@")[-1]
            .split(",")[0]
        )
        longitude = (
            loc_dom.xpath('//a[contains(@href, "maps")]/@href')[0]
            .split("@")[-1]
            .split(",")[1]
        )
        hours_of_operation = []
        hoo = loc_dom.xpath('//div[@class="directory-store-hours"]//text()')
        hoo = [elem.strip() for elem in hoo if elem.strip()]
        for elem in hoo:
            clear_elem = " ".join([e.strip() for e in elem.split()])
            hours_of_operation.append(clear_elem)
        hours_of_operation = (
            ", ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
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
