import re
import csv
import json
from lxml import etree
from time import sleep
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

    start_url = "https://www.netcostmarket.com/locations/"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")

    with SgFirefox() as driver:
        driver.get(start_url)
        dom = etree.HTML(driver.page_source)

    all_locations = dom.xpath('//a[@class="stores_location-el-address"]/@href')
    for url in all_locations:
        store_url = urljoin(start_url, url)
        with SgFirefox() as driver:
            driver.get(store_url)
            sleep(20)
            loc_dom = etree.HTML(driver.page_source)
        poi = loc_dom.xpath('//script[contains(text(), "latitude")]/text()')
        if poi:
            poi = json.loads(poi[0])
            location_name = poi["name"]
            street_address = poi["address"]["streetAddress"]
            city = poi["address"]["addressLocality"]
            state = poi["address"]["addressRegion"]
            zip_code = poi["address"]["postalCode"]
            country_code = poi["address"]["addressCountry"]
            store_number = "<MISSING>"
            phone = poi["address"]["telephone"]
            location_type = "<MISSING>"
            latitude = poi["geo"]["latitude"]
            longitude = poi["geo"]["longitude"]
            hoo = []
            if type(poi["openingHoursSpecification"]) == list:
                for d in poi["openingHoursSpecification"]:
                    for day in d["dayOfWeek"]:
                        opens = d["opens"]
                        closes = d["closes"]
                        hoo.append(f"{day} {opens} - {closes}")
            else:
                for day in poi["openingHoursSpecification"]["dayOfWeek"]:
                    opens = poi["openingHoursSpecification"]["opens"]
                    closes = poi["openingHoursSpecification"]["closes"]
                    hoo.append(f"{day} {opens} - {closes}")
            hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"
        else:
            poi = loc_dom.xpath('//script[@type="application/ld+json"]/text()')[0]
            poi = json.loads(poi)
            all_poi = poi["address"]
            location_name = loc_dom.xpath("//h1/text()")
            location_name = "".join(location_name) if location_name else "<MISSING>"
            raw_address = loc_dom.xpath(
                '//div[@data-widget_type="text-editor.default"]/div/div/p/text()'
            )[:2]
            addr = parse_address_intl(" ".join(raw_address))
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            city = addr.city
            if not city:
                city = raw_address[-1].split(",")[0]
            state = addr.state
            state = state if state else "<MISSING>"
            zip_code = addr.postcode
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = addr.country
            country_code = country_code if country_code else "<MISSING>"
            store_number = "<MISSING>"
            phone = [
                e["telephone"]
                for e in all_poi
                if street_address[:-1] in e["streetAddress"]
            ]
            if not phone:
                phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')
            phone = phone[0] if phone else "<MISSING>"
            location_type = "<MISSING>"
            geo = loc_dom.xpath('//iframe[contains(@src, "/maps/embed")]/@src')
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            if geo:
                geo = geo[0].split("!2d")[-1].split("!2m")[0].split("!3d")
                latitude = geo[-1].split("!")[0]
                longitude = geo[0].split("!")[0]
            hoo = loc_dom.xpath(
                '//div[p[contains(text(), "Monday – Sunday")]]/p//text()'
            )[:2]
            if not hoo:
                hoo = loc_dom.xpath(
                    '//div[p[contains(text(), "Monday – Saturday")]]/p/text()'
                )[:4]
            hoo = [e.strip() for e in hoo if e.strip()]
            hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"
        hours_of_operation = hours_of_operation.split(" u ")[0]

        item = [
            domain,
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
