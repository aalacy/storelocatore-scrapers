import re
import csv
from lxml import etree
from time import sleep
from urllib.parse import urljoin

from sgrequests import SgRequests
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
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []

    start_url = "https://www.canadacomputers.com/location.php"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")

    with SgFirefox() as driver:
        driver.get(start_url)
        sleep(10)
        driver.save_screenshot("canada.png")
        driver.find_element_by_xpath('//button[contains(text(), "English")]').click()
        sleep(10)
        driver.save_screenshot("canada_2.png")
        dom = etree.HTML(driver.page_source)

    all_locations = dom.xpath('//a[contains(@href, "location_details")]/@href')
    for url in all_locations:
        store_url = urljoin(start_url, url)
        print(store_url)
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath(
            '//h1[@class="font-arial text-uppercase text-cc font-weight-bold"]/text()'
        )
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_data = loc_dom.xpath(
            '//h3[contains(text(), "Address")]/following-sibling::div[1]//text()'
        )
        raw_data = [e.strip() for e in raw_data if e.strip()]
        addr = parse_address_intl(" ".join(raw_data[:2]))
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        street_address = street_address if street_address else "<MISSING>"
        city = addr.city
        city = city if city else "<MISSING>"
        state = addr.state
        state = state if state else "<MISSING>"
        zip_code = addr.postcode
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = addr.country
        country_code = country_code if country_code else "<MISSING>"
        store_number = "<MISSING>"
        phone = loc_dom.xpath(
            '//h3[contains(text(), "Address")]/following-sibling::div[1]//a[contains(@href, "tel")]/text()'
        )
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        geo = (
            loc_dom.xpath(
                '//h3[contains(text(), "Address")]/following-sibling::div[1]//a[contains(@href, "maps")]/@href'
            )[0]
            .split("=")[-1]
            .split(",")
        )
        latitude = geo[0]
        longitude = geo[1]
        days = loc_dom.xpath(
            '//h3[contains(text(), "Centre Hours:")]/following-sibling::div[1]/div[1]/ul/li//text()'
        )
        days = [e.strip() for e in days if e.strip()]
        hours = loc_dom.xpath(
            '//h3[contains(text(), "Centre Hours:")]/following-sibling::div[1]/div[2]/ul/li//text()'
        )
        hours = [e.strip() for e in hours if e.strip()]
        hoo = list(map(lambda d, h: d + " " + h, days, hours))
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

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
