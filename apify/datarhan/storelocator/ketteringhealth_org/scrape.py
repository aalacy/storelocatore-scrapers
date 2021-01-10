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

    DOMAIN = "ketteringhealth.org"
    start_url = "https://www.ketteringhealth.org/locations/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath(
        '//h1[contains(text(), "All Locations")]/following-sibling::div[@class="row"]'
    )
    pages = dom.xpath('//div[@class="pagebox"]/a/@href')
    for page in pages:
        response = session.get(urljoin(start_url, page))
        dom = etree.HTML(response.text)
        all_locations += dom.xpath(
            '//h1[contains(text(), "All Locations")]/following-sibling::div[@class="row"]'
        )

    for poi_html in all_locations:
        store_url = "<MISSING>"
        store_url = store_url if store_url else "<MISSING>"
        location_name = poi_html.xpath('.//h1[@class="locnamebig"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_address = poi_html.xpath('.//div[@class="locaddress"]/text()')
        raw_address = [elem.strip() for elem in raw_address if elem.strip()]
        if len(raw_address) == 2:
            raw_address = [raw_address[0]] + raw_address[1].split(", ")
        if len(raw_address) == 4:
            raw_address = [", ".join(raw_address[:3])] + raw_address[-1].split(", ")
        if len(raw_address) == 3:
            if ", " in raw_address[-1]:
                raw_address = [", ".join(raw_address[:2])] + raw_address[-1].split(", ")
        street_address = raw_address[0]
        street_address = street_address if street_address else "<MISSING>"
        city = raw_address[1].split(",")[0]
        city = city if city else "<MISSING>"
        state = raw_address[-1].split()[0]
        state = state if state else "<MISSING>"
        zip_code = raw_address[-1].split()[-1]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = poi_html.xpath('.//strong[abbr[@title="Phone"]]/text()')
        phone = phone[0].strip() if phone else "<MISSING>"
        location_type = "<MISSING>"
        geo = (
            poi_html.xpath('.//iframe[@title="Google Map"]/@src')[0]
            .split("=")[1]
            .split("&")[0]
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
        check = f"{location_name} {street_address}"
        if check not in scraped_items:
            scraped_items.append(check)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
