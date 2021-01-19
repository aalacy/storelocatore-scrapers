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

    DOMAIN = "beefeater.co.uk"
    start_url = "https://www.beefeater.co.uk/en-gb/locations"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//a[@class="title-text"]/@href')

    for url in list(set(all_locations)):
        store_url = urljoin(start_url, url)
        if len(store_url.split("/")) == 6:
            continue
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        raw_address = loc_dom.xpath("//address//text()")
        raw_address = [elem.strip() for elem in raw_address if elem.strip()]
        if not raw_address:
            continue
        location_name = loc_dom.xpath(
            '//h1[@class="h1 title-text brand-header light"]/text()'
        )
        location_name = location_name[0].strip() if location_name else "<MISSING>"
        street_address = raw_address[0]
        if street_address.endswith(","):
            street_address = street_address[:-1]
        city = raw_address[1]
        if city.endswith(","):
            city = city[:-1]
        state = raw_address[2]
        if state.endswith(","):
            state = state[:-1]
        zip_code = raw_address[3]
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = loc_dom.xpath(
            '//a[@class="details--table-cell__phone icon__phone"]/text()'
        )
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = loc_dom.xpath(
            '//div[@class="cmp-locationdetails__info-container clearfix"]/div[1]//p/text()'
        )
        hours_of_operation = [elem.strip() for elem in hours_of_operation]
        hours_of_operation = (
            " ".join(hours_of_operation).split("  ")[0]
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
