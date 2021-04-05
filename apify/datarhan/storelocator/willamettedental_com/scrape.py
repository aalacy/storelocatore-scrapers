import csv
from urllib.parse import urljoin
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
    scraped_items = []

    DOMAIN = "willamettedental.com"
    start_urls = [
        "https://locations.willamettedental.com/search.html?q=Seattle%2C+WA&r=3000&languages=",
        "https://locations.willamettedental.com/search.html?q=Twin+Falls%2C+ID&r=3000&languages=",
    ]
    for start_url in start_urls:
        response = session.get(start_url)
        dom = etree.HTML(response.text)

        all_locations = dom.xpath('//article[@class="location-card"]')
        for poi_html in all_locations:
            store_url = poi_html.xpath('.//a[@data-ya-track="office_page_link"]/@href')
            store_url = urljoin(start_url, store_url[0]) if store_url else "<MISSING>"
            loc_response = session.get(store_url)
            loc_dom = etree.HTML(loc_response.text)

            location_name = poi_html.xpath(
                './/a[@class="location-card-titleLink"]/text()'
            )
            location_name = location_name[0] if location_name else "<MISSING>"
            street_address = poi_html.xpath(
                './/span[@class="c-address-street-1"]/text()'
            )
            street_address = street_address[0] if street_address else "<MISSING>"
            city = poi_html.xpath('.//span[@class="c-address-city"]/span/text()')
            city = city[0] if city else "<MISSING>"
            state = poi_html.xpath('.//abbr[@class="c-address-state"]/text()')
            state = state[0] if state else "<MISSING>"
            zip_code = poi_html.xpath('.//span[@class="c-address-postal-code"]/text()')
            zip_code = zip_code[0].strip() if zip_code else "<MISSING>"
            store_number = loc_dom.xpath("//@itemid")[0]
            phone = loc_dom.xpath('//span[@itemprop="telephone"]/text()')
            phone = phone[0][1:-1] if phone else "<MISSING>"
            country_code = loc_dom.xpath(".//address/@data-country")[0]
            location_type = loc_dom.xpath("//main/@itemtype")[0].split("/")[-1]
            latitude = loc_dom.xpath('//meta[@itemprop="latitude"]/@content')
            latitude = latitude[0] if latitude else "<MISSING>"
            longitude = loc_dom.xpath('//meta[@itemprop="longitude"]/@content')
            longitude = longitude[0] if longitude else "<MISSING>"
            hours_of_operation = loc_dom.xpath(
                '//div[@class="c-location-hours"]//table[@class="c-location-hours-details"]//text()'
            )[2:]
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
            if store_number not in scraped_items:
                scraped_items.append(store_number)
                items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
