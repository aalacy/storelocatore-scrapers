# -*- coding: utf-8 -*-
import re
import json
from lxml import etree
from urllib.parse import urljoin

from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgFirefox
from sgzip.dynamic import DynamicZipSearch, SearchableCountries


def fetch_data():
    start_url = "https://www.bipa.at/filialen"
    domain = "bipa.at"

    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.AUSTRIA], expected_search_radius_miles=50
    )
    with SgFirefox(is_headless=False) as driver:
        for code in all_codes:
            driver.get(start_url)
            try:
                driver.find_element_by_xpath(
                    '//button[contains(text(), "Cookies erlauben")]'
                ).click()
            except Exception:
                pass
            driver.find_element_by_id("addressstring").send_keys(code)
            driver.find_element_by_id("findButton").click()
            dom = etree.HTML(driver.page_source)

            all_locations = dom.xpath("//@data-options")
            try:
                count = 0
                next_page = driver.find_element_by_class_name("next_link")
                while next_page:
                    if count > 9:
                        break
                    next_page.click()
                    dom = etree.HTML(driver.page_source)
                    all_locations += dom.xpath("//@data-options")
                    next_page = driver.find_element_by_class_name("next_link")
                    count += 1
            except Exception:
                pass

            for poi in all_locations:
                print(poi)
                poi = poi.replace("null", '""')
                if poi.startswith("["):
                    continue
                if len(poi.strip()) < 10:
                    continue
                location_name = re.findall(r'name":"(.+?)",', poi)[0]
                page_url = "https://www.bipa.at/filialen"
                street_address = re.findall(r'address1":"(.+?)",', poi)[0]
                city = re.findall(r'city":"(.+?)",', poi)[0]
                state = re.findall(r'stateCode":"(.+?)",', poi)[0]
                zip_code = re.findall(r'postalCode":"(.+?)",', poi)[0]
                phone = re.findall(r'phone":"(.+?)",', poi)[0]
                hoo = re.findall(r'storeHours":"(.+?\})"', poi)[0].replace("\\", "")
                hoo = json.loads(hoo)
                hours = []
                for d, h in hoo.items():
                    if h:
                        hours.append(f"{d}: {h[0]}")
                    else:
                        hours.append(f"{d}: closed")
                hours = ", ".join(hours)
                page_url = re.findall('url":"(.+?)",', poi)[0][0]
                page_url = urljoin(start_url, page_url)
                store_number = re.findall('storeid":"(.+?)"', poi)[0]
                latitude = re.findall('latitude":(.+?),', poi)[0]
                longitude = re.findall('longitude":(.+?),', poi)[0]

                item = SgRecord(
                    locator_domain=domain,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zip_code,
                    country_code="AT",
                    store_number=store_number,
                    phone=phone,
                    location_type="",
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours,
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
