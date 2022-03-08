# -*- coding: utf-8 -*-
import ssl
from time import sleep
from lxml import etree

from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sgselenium.sgselenium import SgFirefox

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context


def fetch_data():
    start_url = "https://pharmacy.jewelosco.com/joweb/#/store"
    domain = "pharmacy.jewelosco.com"

    all_coords = DynamicZipSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=100
    )
    with SgFirefox() as driver:
        for code in all_coords:
            all_poi_html = []

            driver.get(start_url)
            sleep(30)
            driver.find_element_by_id("searchData").send_keys(code)
            driver.find_element_by_id("submitbutton").click()
            sleep(5)
            all_locations = driver.find_elements_by_xpath(
                '//button[contains(text(), "Store details")]'
            )
            for i, loc in enumerate(all_locations):
                all_locations[i].click()
                sleep(5)
                all_poi_html.append(etree.HTML(driver.page_source))
                try:
                    driver.back()
                except Exception:
                    sleep(120)
                    driver.back()
                sleep(5)
                all_locations = driver.find_elements_by_xpath(
                    '//button[contains(text(), "Store details")]'
                )
            try:
                next_page = driver.find_element_by_xpath(
                    '//li[@class="pagination-next ng-scope"]/a'
                )
            except Exception:
                next_page = ""
            if next_page:
                next_page.click()
                sleep(10)
                all_locations = driver.find_elements_by_xpath(
                    '//button[contains(text(), "Store details")]'
                )
                for i, loc in enumerate(all_locations):
                    all_locations[i].click()
                    sleep(10)
                    all_poi_html.append(etree.HTML(driver.page_source))
                    driver.back()
                    sleep(10)
                    next_page = driver.find_element_by_xpath(
                        '//li[@class="pagination-next ng-scope"]/a'
                    )
                    next_page.click()
                    sleep(10)
                    all_locations = driver.find_elements_by_xpath(
                        '//button[contains(text(), "Store details")]'
                    )
            try:
                next_page = driver.find_element_by_xpath(
                    '//li/a[contains(text(), "3")]'
                )
            except Exception:
                next_page = ""
            if next_page:
                next_page.click()
                sleep(10)
                all_locations = driver.find_elements_by_xpath(
                    '//button[contains(text(), "Store details")]'
                )
                for i, loc in enumerate(all_locations):
                    try:
                        all_locations[i].click()
                    except Exception:
                        continue
                    sleep(10)
                    all_poi_html.append(etree.HTML(driver.page_source))
                    driver.back()
                    sleep(10)
                    next_page = driver.find_element_by_xpath(
                        '//li/a[contains(text(), "3")]'
                    )
                    next_page.click()
                    sleep(10)
                    all_locations = driver.find_elements_by_xpath(
                        '//button[contains(text(), "Store details")]'
                    )

            for poi_html in all_poi_html:
                location_name = poi_html.xpath("//address/strong/text()")
                if not location_name:
                    continue
                location_name = location_name[0]
                raw_data = poi_html.xpath(
                    '//address[@class="storeDetails-address ng-binding"]/text()'
                )
                raw_data = [e.strip() for e in raw_data if e.strip()]
                hoo = poi_html.xpath(
                    '//tr[@ng-repeat="stores_hrs in storeDetailsResponse.hours"]//text()'
                )
                hoo = " ".join([e.strip() for e in hoo if e.strip()])
                geo = (
                    poi_html.xpath(
                        '//iframe[@class="storeDetails-loc-dir-map-frame"]/@src'
                    )[0]
                    .split("q=")[-1]
                    .split("&")[0]
                    .split("%2C")
                )

                item = SgRecord(
                    locator_domain=domain,
                    page_url=start_url,
                    location_name=location_name,
                    street_address=location_name,
                    city=raw_data[0].split(", ")[0],
                    state=raw_data[0].split(", ")[-1].split()[0],
                    zip_postal=raw_data[0].split(", ")[-1].split()[-1],
                    country_code="",
                    store_number="",
                    phone=raw_data[-1],
                    location_type="",
                    latitude=geo[0],
                    longitude=geo[1],
                    hours_of_operation=hoo,
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
