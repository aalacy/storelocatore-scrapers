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
    items = []

    session = SgRequests()

    DOMAIN = "yvesrocher.ca"
    start_url = "https://www.yvesrocher.ca/en/all-about-our-stores/stores-and-spa/SL"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    data = dom.xpath('//script[contains(text(), "dataLayerOptions")]/text()')[0]
    data = re.findall('hrefu003d"(.+?)"u003e', data.replace("\\", ""))
    all_locations = [elem for elem in data if "all-about-our" in elem]

    for url in all_locations:
        store_url = urljoin(start_url, url)
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        data = loc_dom.xpath('//script[contains(text(), "dataLayerOptions")]/text()')[0]
        data = data.replace("u003c", "<").replace("u003d", "=").replace("u003e", ">")
        loc_dom = etree.HTML(re.findall('html":"(.+?)","js', data.replace("\\", ""))[0])

        location_name = loc_dom.xpath('//meta[@itemprop="name"]/@content')[0]
        street_address = loc_dom.xpath('//meta[@itemprop="streetAddress"]/@content')
        street_address = (
            street_address[0]
            .replace("u0027", "'")
            .replace("u00E9", "é")
            .replace("u00E8", "è")
            .replace("u00F4", "ô")
            if street_address
            else "<MISSING>"
        )
        city = loc_dom.xpath('//meta[@itemprop="addressLocality"]/@content')
        city = city[0] if city[0].strip() else "<MISSING>"
        state = "<MISSING>"
        zip_code = loc_dom.xpath('//meta[@itemprop="postalCode"]/@content')
        zip_code = zip_code[0] if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = loc_dom.xpath('//meta[@itemprop="telephone"]/@content')
        phone = phone[0] if phone else "<MISSING>"
        location_type = loc_dom.xpath("//div/@itemtype")[0].split("/")[-1]
        latitude = loc_dom.xpath('//meta[@itemprop="latitude"]/@content')
        latitude = latitude[0] if latitude else "<MISSING>"
        longitude = loc_dom.xpath('//meta[@itemprop="longitude"]/@content')
        longitude = longitude[0] if longitude else "<MISSING>"
        hours_of_operation = loc_dom.xpath('//table[@class="horaire-table"]//text()')
        hours_of_operation = (
            " ".join([elem.strip() for elem in hours_of_operation])
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

        items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
