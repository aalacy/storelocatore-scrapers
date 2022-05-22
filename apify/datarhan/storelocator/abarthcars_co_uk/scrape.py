# -*- coding: utf-8 -*-
from lxml import etree
from time import sleep
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgChrome
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sgpostal.sgpostal import parse_address_intl
import os
import ssl

domain = "abarthcars.co.uk"
logger = sglog.SgLogSetup().get_logger(logger_name=domain)

os.environ[
    "PROXY_URL"
] = "http://groups-RESIDENTIAL,country-gb:{}@proxy.apify.com:8000/"

ssl._create_default_https_context = ssl._create_unverified_context


def fetch_data():
    start_url = "https://www.abarthcars.co.uk/retailers"

    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.BRITAIN], expected_search_radius_miles=100
    )
    with SgChrome() as driver:
        for code in all_codes:
            driver.get(start_url)
            sleep(3)
            try:
                driver.switch_to.frame(
                    driver.find_element_by_xpath('//iframe[@id="iFrame1"]')
                )
                driver.find_element_by_xpath('//button[@id="decline-text"]').click()
                driver.switch_to.default_content()
            except Exception:
                pass
            sleep(2)
            elem = driver.find_element_by_xpath('//input[@name="search_address"]')
            elem.send_keys(code)
            sleep(3)
            try:
                elem = driver.find_element_by_xpath('//div[@class="pac-item"]')
            except Exception:
                continue
            elem.click()
            sleep(10)
            dom = etree.HTML(driver.page_source)

            all_locations = dom.xpath('//div[@class="results-item"]')
            logger.info(f"Zipcode: {code} => Total Locations: {len(all_locations)-1}")
            for poi_html in all_locations:
                location_name = (
                    poi_html.xpath('.//div[@class="dl_name"]/text()')[0]
                    .strip()
                    .replace(".", "")
                )
                street_address = poi_html.xpath(
                    './/div[@class="dl_address"]/strong/text()'
                )
                if not street_address:
                    continue
                street_address = " ".join(street_address[0].split())
                raw_data = (
                    poi_html.xpath('.//div[@class="dl_address"]/text()')[0]
                    .replace("_", " ")
                    .strip()
                )
                addr = parse_address_intl(raw_data)
                phone = poi_html.xpath('.//a[contains(@href, "tel")]/text()')[0].strip()
                if phone == "null":
                    phone = ""
                hoo = poi_html.xpath(
                    './/p[contains(text(), "Opening hours")]/following-sibling::p/strong/text()'
                )
                hoo = " ".join(hoo) if hoo else ""
                zip_code = addr.postcode
                if not zip_code:
                    zip_code = " ".join(raw_data.split()[:2])
                city = addr.city
                if not city:
                    city = " ".join(raw_data.split()[2:]).split(",")[0].split("(")[0]

                item = SgRecord(
                    locator_domain=domain,
                    page_url=start_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=addr.state,
                    zip_postal=zip_code,
                    country_code="",
                    store_number="",
                    phone=phone,
                    location_type="",
                    latitude="",
                    longitude="",
                    hours_of_operation=hoo,
                    raw_address=raw_data,
                )

                yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
