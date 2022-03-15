import re
import csv
import json
import demjson
import yaml
from lxml import etree
from urllib.parse import urljoin

from sgselenium import SgFirefox
from sgscrape.sgpostal import parse_address_intl


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

    DOMAIN = "sixt.co.uk"
    start_url = "https://www.sixt.co.uk/car-hire/united-kingdom/"

    all_locations = []
    with SgFirefox() as driver:
        driver.get(start_url)
        dom = etree.HTML(driver.page_source)

        all_cities = dom.xpath('//div[@class="swiper-wrapper"]/a/@href')
        for url in all_cities:
            driver.get(urljoin(start_url, url))
            dom = etree.HTML(driver.page_source)
            data = dom.xpath('//script[contains(text(), "googleMarkers")]/text()')[0]
            data = re.findall("googleMarkers =(.+);", data)[0]
            data = yaml.load(data.replace("' + '", ""))
            for elem in data:
                all_locations.append(elem["locationLink"])

    for url in all_locations:
        store_url = urljoin(start_url, url)
        with SgFirefox() as driver:
            driver.get(store_url)
            loc_dom = etree.HTML(driver.page_source)
        poi = loc_dom.xpath('//script[contains(text(), "mainEntityOfPage")]/text()')
        if poi:
            poi = json.loads(poi[0])

            location_name = poi["name"]
            location_name = location_name if location_name else "<MISSING>"
            street_address = poi["address"]["streetAddress"]
            street_address = street_address if street_address else "<MISSING>"
            city = poi["address"]["addressLocality"]
            city = city if city else "<MISSING>"
            state = "<MISSING>"
            zip_code = poi["address"]["postalCode"]
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = poi["address"]["addressRegion"]
            store_number = "<MISSING>"
            phone = "<MISSING>"
            location_type = poi["@type"]
            latitude = poi["geo"]["latitude"]
            longitude = poi["geo"]["longitude"]
            hoo = poi["openingHours"]
            hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"
        else:
            location_name = loc_dom.xpath(
                '//span[@class="dropdown-block_title-copy"]/text()'
            )
            location_name = location_name[0] if location_name else "<MISSING>"
            raw_address = loc_dom.xpath(
                '//div[h3[contains(text(), "location address")]]/following-sibling::div[1]/p/text()'
            )[0]
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            street_address = street_address if street_address else "<MISSING>"
            city = addr.city
            city = city if city else "<MISSING>"
            state = "<MISSING>"
            zip_code = addr.postcode
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = loc_dom.xpath('//meta[@name="countrycode"]/@content')
            country_code = country_code[0] if country_code else "<MISSING>"
            store_number = "<MISSING>"
            phone = "<MISSING>"
            location_type = "<MISSING>"

            data = loc_dom.xpath('//script[contains(text(), "googleMarkers")]/text()')[
                0
            ]
            data = re.findall("googleMarkers = (.+);", data)[0]
            data = demjson.decode(data.replace("' + '", ""))
            for e in data:
                if e["locationName"] == location_name:
                    geo = e["coordinates"]
                    break
            latitude = geo["lat"]
            longitude = geo["lng"]
            hoo = loc_dom.xpath('//div[@class="openhours-scheduler"]//text()')
            hoo = [elem.strip() for elem in hoo if elem.strip()]
            hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"
        hours_of_operation = hours_of_operation.replace("24 HRS RETURN ", "")

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
