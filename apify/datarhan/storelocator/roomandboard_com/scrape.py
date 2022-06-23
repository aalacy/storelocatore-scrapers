import re
import ssl
import json
from lxml import etree
from time import sleep
from urllib.parse import urljoin

from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


def fetch_data():
    domain = "roomandboard.com"
    start_url = "https://www.roomandboard.com/stores/"

    with SgChrome() as driver:
        driver.get(start_url)
        try:
            driver.find_element_by_xpath('//button[contains(text(), "See")]').click()
            sleep(2)
            driver.find_element_by_xpath('//button[@id="submit"]').click()
            sleep(10)
        except Exception:
            pass
        dom = etree.HTML(driver.page_source)

        all_locations = dom.xpath('//a[contains(@href, "stores/")]/@href')
        for url in all_locations:
            store_url = urljoin("https://www.roomandboard.com", url)
            driver.get(store_url)
            loc_dom = etree.HTML(driver.page_source)
            poi = loc_dom.xpath('//script[@id="store-schema-data"]/text()')[0]
            poi = json.loads(poi)

            location_name = poi["name"]
            street_address = poi["address"]["streetAddress"]
            if not street_address:
                continue
            city = poi["address"]["addressLocality"]
            state = poi["address"]["addressRegion"]
            zip_code = poi["address"]["postalCode"]
            phone = poi.get("telephone")
            location_type = poi["@type"]
            geo = loc_dom.xpath('//a[contains(@href, "/@")]/@href')
            latitude = ""
            longitude = ""
            if geo:
                geo = geo[-1].split("/@")[-1].split(",")[:2]
                latitude = geo[0]
                longitude = geo[1]
            hoo = loc_dom.xpath(
                '//div[contains(@class, "storeDetails_StoreDetailsHours")]//li[span[@class="hours_HoursDay__D_ako"]]//text()'
            )
            hoo = [elem.strip() for elem in hoo if elem.strip()]
            hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"
            store_number = re.findall('storeNumber":"(.+?)",', driver.page_source)[0]

            if "," in city:
                state = city.split(", ")[-1]
                city = city.split(",")[0]

            item = SgRecord(
                locator_domain=domain,
                page_url=store_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code="",
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
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
