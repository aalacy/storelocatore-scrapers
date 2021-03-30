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
    session = SgRequests().requests_retry_session(retries=1, backoff_factor=0.3)

    items = []

    DOMAIN = "splendid.com"
    start_url = "https://www.splendid.com/store-locations"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//div[@class="spl-store-locator__store"]')

    for poi_html in all_locations:
        store_url = poi_html.xpath(
            './/a[@class="spl-store-locator__store__directions"]/@href'
        )[0]
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = poi_html.xpath("@data-store")
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_address = poi_html.xpath(
            './/span[@class="spl-store-locator__store__address-line"]/text()'
        )
        street_address = raw_address[0]
        city = raw_address[1].split(", ")[0]
        state = raw_address[1].split(", ")[-1].split()[0]
        zip_code = raw_address[1].split(", ")[-1].split()[-1]
        country_code = "<MISSING>"
        if "United States" in loc_dom.xpath("//address/text()")[-1]:
            country_code = "United States"
        store_number = "<MISSING>"
        phone = poi_html.xpath('.//div[@class="spl-store-locator__store__tel"]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = loc_dom.xpath("//@data-lat")[0]
        longitude = loc_dom.xpath("//@data-long")[0]
        hoo = loc_dom.xpath(
            '//aside[@class="store-workhours"]//div[@data-role="content"]//text()'
        )
        hoo = [elem.strip() for elem in hoo if elem.strip()]
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
