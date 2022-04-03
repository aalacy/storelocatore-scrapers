import csv
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl
from sgzip.dynamic import DynamicZipSearch, SearchableCountries


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

    DOMAIN = "jamesavery.com"
    start_url = "https://www.jamesavery.com/store_locations?utf8=%E2%9C%93&distance=any&address={}&store_type%5B%5D=retail&authenticity_token=yEwudnl2zo%2FdiLBCZIncYa3relP0t3%2FZPLiT4xG8SaJbVKaPckX7qzA1x6Ve%2F1uMa2N2xOUCG0%2FlPJcccmfIoA%3D%3D"

    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA], max_search_distance_miles=500
    )
    for code in all_codes:
        response = session.get(start_url.format(code))
        dom = etree.HTML(response.text)
        all_locations = dom.xpath('//li[@itemtype="http://schema.org/Place"]')

        for poi_html in all_locations:
            store_url = poi_html.xpath('.//h3[@itemprop="name"]/a/@href')
            store_url = urljoin(start_url, store_url[0]) if store_url else "<MISSING>"
            location_name = poi_html.xpath('.//h3[@itemprop="name"]/a/text()')
            location_name = location_name[0] if location_name else "<MISSING>"
            address_raw = poi_html.xpath('.//span[@itemprop="address"]/text()')[0]
            addr = parse_address_intl(address_raw)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            state = addr.state
            state = state if state else "<MISSING>"
            city = addr.city
            city = city if city else "<MISSING>"
            zip_code = addr.postcode
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = addr.country
            country_code = country_code if country_code else "<MISSING>"
            store_number = "<MISSING>"
            phone = poi_html.xpath('.//a[@itemprop="telephone"]/text()')
            phone = phone[0] if phone else "<MISSING>"
            location_type = "<MISSING>"
            geo = (
                poi_html.xpath('.//a[@itemprop="map"]/@href')[0]
                .split("=")[1]
                .split("&")[0]
                .split("%2C")
            )
            latitude = geo[0]
            longitude = geo[1]
            hours_of_operation = poi_html.xpath('.//div[@class="store"]//text()')
            hours_of_operation = [
                elem.strip() for elem in hours_of_operation if "p.m." in elem
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

            if store_url not in scraped_items:
                scraped_items.append(store_url)
                items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
