import re
import csv
import ssl
from lxml import etree
from time import sleep
from urllib.parse import urljoin

from sgselenium import SgChrome
from sgscrape.sgpostal import parse_address_intl

from sglogging import SgLogSetup

ssl._create_default_https_context = ssl._create_unverified_context

logger = SgLogSetup().get_logger("caraluzzis.com")


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

    start_url = "https://caraluzzis.com/locations/"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")

    with SgChrome() as driver:
        driver.get(start_url)
        dom = etree.HTML(driver.page_source)

        all_locations = dom.xpath('//div[@class="fl-rich-text"]/p/a[strong]')
        for poi_html in all_locations:
            store_url = urljoin(start_url, poi_html.xpath("@href")[0])
            if "https://store.caraluzzis.com/" in store_url:
                continue
            location_name = poi_html.xpath(".//strong/text()")
            location_name = location_name[0] if location_name else "<MISSING>"
            logger.info(f"Location Name: {location_name}")
            logger.info(f"Page URL: {store_url}")
            if "WINE & SPIRITS" in location_name:
                continue

            driver.get(store_url)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            iframe = driver.find_element_by_xpath('//div[@class="fl-map"]/iframe')
            driver.switch_to.frame(iframe)
            sleep(15)
            loc_dom = etree.HTML(driver.page_source)
            geo = (
                loc_dom.xpath('//a[@class="navigate-link"]/@href')[0]
                .split("ll=")[-1]
                .split("&")[0]
                .split(",")
            )
            driver.switch_to.default_content()
            loc_dom = etree.HTML(driver.page_source)

            raw_address = (
                loc_dom.xpath("//iframe/@src")[0]
                .split("q=")[-1]
                .split("&")[0]
                .replace("+", " ")
                .replace("%2C", "")
            )
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            city = addr.city
            city = city if city else "<MISSING>"
            state = addr.state
            state = state if state else "<MISSING>"
            zip_code = addr.postcode
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = addr.country
            country_code = country_code if country_code else "<MISSING>"
            store_number = "<MISSING>"
            phone = (
                loc_dom.xpath('//h5[@class="fl-heading"]/span/text()')[0]
                .split("•")[1]
                .strip()
            )
            location_type = "<MISSING>"
            latitude = geo[0]
            longitude = geo[1]
            hours_of_operation = (
                loc_dom.xpath('//h5[@class="fl-heading"]/span/text()')[0]
                .split("•")[2]
                .split("- Temp Hours")[0]
                .strip()
            )

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
