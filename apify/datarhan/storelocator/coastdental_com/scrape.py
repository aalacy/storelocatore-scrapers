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

    DOMAIN = "coastdental.com"
    start_url = "https://www.coastdental.com/locations/all-coast-dental-offices"
    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="locationsEntry"]')
    for poi_html in all_locations:
        url = poi_html.xpath('.//a[@class="calloutBoxLink1"]/@href')[0]
        store_url = urljoin(start_url, url)
        location_name = poi_html.xpath('.//div[@class="officeName"]/h2/text()')
        location_name = location_name[0].strip() if location_name else "<MISSING>"
        address_raw = poi_html.xpath('.//div[@class="officeName"]/text()')
        address_raw = [elem.strip() for elem in address_raw if elem.strip()]
        if len(address_raw) == 3:
            address_raw = [", ".join(address_raw[:2])] + address_raw[2:]
        street_address = address_raw[0]
        city = address_raw[1].split(",")[0]
        state = address_raw[1].split(",")[-1].split()[0]
        zip_code = address_raw[1].split(",")[-1].split()[-1]
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = poi_html.xpath(".//h3/text()")
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        if "closed" in location_name.lower():
            location_type = "closed"

        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        latitude = loc_dom.xpath('.//meta[@itemprop="latitude"]/@content')[0]
        longitude = loc_dom.xpath('.//meta[@itemprop="longitude"]/@content')[0]
        hours_of_operation = poi_html.xpath('.//div[@class="leftColDayHours"]//text()')
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
