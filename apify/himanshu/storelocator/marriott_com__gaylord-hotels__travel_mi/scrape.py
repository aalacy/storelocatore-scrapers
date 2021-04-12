import re
import csv
import json
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

    start_url = "https://www.marriott.com/"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")

    with SgFirefox() as driver:
        driver.get(start_url)
        sleep(5)
        driver.find_element_by_xpath('//a[@data-component-name="mainNavLink"]').click()
        sleep(10)
        dest = driver.find_element_by_xpath(
            '//a[contains(text(), "Browse by Destination")]'
        )
        driver.execute_script("arguments[0].scrollIntoView();", dest)
        dest.click()
        sleep(5)
        us = driver.find_element_by_xpath(
            '//a[contains(text(), "View all hotels in the United States")]'
        )
        driver.execute_script("arguments[0].scrollIntoView();", us)
        us.click()
        sleep(10)
        brand = driver.find_element_by_xpath(
            '//div[@class="tile-search-filter l-float-right "]//span[@data-target="brands"]'
        )
        driver.find_element_by_xpath(
            '//div[@class="tile-search-filter l-float-right "]'
        ).click()
        driver.execute_script("arguments[0].scrollIntoView();", brand)
        brand.click()
        sleep(5)
        filter_brand = driver.find_element_by_xpath(
            '//span[contains(text(), "Gaylord Hotels")]'
        )
        sleep(5)
        driver.execute_script("arguments[0].scrollIntoView();", filter_brand)
        sleep(5)
        filter_brand.click()
        sleep(5)
        apply_button = driver.find_element_by_xpath(
            '//form[@class="js-submit-form"]//button[contains(text(), "Apply")]'
        )
        driver.execute_script("arguments[0].scrollIntoView();", apply_button)
        apply_button.click()
        sleep(5)
        dom = etree.HTML(driver.page_source)

    all_locations = dom.xpath('//a[@class="t-alt-link analytics-click"]/@href')
    for url in all_locations:
        store_url = "https://www.marriott.com/hotels/travel/" + url.split("/")[-2] + "/"
        store_url = urljoin(start_url, store_url)
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        poi = loc_dom.xpath('//script[@data-component-name="schemaOrg"]/text()')
        if poi:
            poi = json.loads(poi[0])
            poi = [e for e in poi["@graph"] if e["@type"] == "Hotel"][0]

            location_name = poi["name"]
            location_name = location_name if location_name else "<MISSING>"
            street_address = poi["address"]["streetAddress"]
            city = poi["address"]["addressLocality"]
            state = poi["address"]["addressRegion"]
            zip_code = poi["address"]["postalCode"]
            country_code = poi["address"]["addressCountry"]
            store_number = "<MISSING>"
            phone = poi["telephone"]
            phone = phone if phone else "<MISSING>"
            location_type = poi["@type"]
            latitude = poi["geo"]["latitude"]
            longitude = poi["geo"]["longitude"]
        else:
            location_name = loc_dom.xpath(
                '//h3[contains(text(), "Getting Here")]/following-sibling::div[1]/p[1]/text()'
            )
            location_name = location_name[0] if location_name else "<MISSING>"
            raw_address = loc_dom.xpath(
                '//h3[contains(text(), "Getting Here")]/following-sibling::div[1]/p[2]/text()'
            )[0]
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            city = addr.city
            state = addr.state
            zip_code = addr.postcode
            country_code = addr.country
            store_number = "<MISSING>"
            phone = loc_dom.xpath('//a[@class="custom_click_track"]/text()')
            phone = phone[0] if phone else "<MISSING>"
            location_type = "Hotel"
            geo = re.findall('lat_long":"(.+?)",', loc_response.text)[0].split(",")
            latitude = geo[0]
            longitude = geo[1]
        hours_of_operation = "<MISSING>"

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
