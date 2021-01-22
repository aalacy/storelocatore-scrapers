import csv
from lxml import etree
import usaddress
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

    DOMAIN = "jamesavery.com"
    start_url = "https://www.jamesavery.com/store_locations?utf8=%E2%9C%93&distance=any&address=&store_type%5B%5D=retail&store_type%5B%5D=dillards&authenticity_token=vz2xpftolQGiScBsgF45%2FJzf0ZicSAQvqTFZ4WRX116lmSE%2FLH9DpO9SStHbU9GlbMUTZOnLC%2FHThlTaTI6RtA%3D%3D"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//li[@itemtype="http://schema.org/Place"]')

    for poi_html in all_locations:
        store_url = poi_html.xpath('.//h3[@itemprop="name"]/a/@href')
        store_url = urljoin(start_url, store_url[0]) if store_url else "<MISSING>"
        location_name = poi_html.xpath('.//h3[@itemprop="name"]/a/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        address_raw = poi_html.xpath('.//span[@itemprop="address"]/text()')[0]
        address_raw = usaddress.tag(address_raw)[0]
        AddressNumber = address_raw["AddressNumber"]
        StreetName = address_raw["StreetName"]
        StreetNamePostType = address_raw.get("StreetNamePostType")
        StreetNamePostType = StreetNamePostType if StreetNamePostType else " "
        street_address = f"{AddressNumber} {StreetName} {StreetNamePostType}".replace(
            "  ", " "
        )
        state = address_raw["StateName"]
        city = address_raw["PlaceName"]
        zip_code = address_raw["ZipCode"]
        country_code = "<MISSING>"
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

        items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
