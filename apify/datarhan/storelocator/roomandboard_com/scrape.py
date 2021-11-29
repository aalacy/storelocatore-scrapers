import ssl
import json
from lxml import etree
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
            driver.find_element_by_xpath('//button[@id="submit"]').click()
        except Exception:
            pass
        dom = etree.HTML(driver.page_source)

        all_locations = dom.xpath(
            '//li[contains(@class, "Heading Heading--4")]/a/@href'
        )
        for url in all_locations:
            store_url = urljoin("https://www.roomandboard.com", url)
            driver.get(store_url)
            loc_dom = etree.HTML(driver.page_source)
            poi = loc_dom.xpath('//script[@id="store-schema-data"]/text()')[0]
            poi = json.loads(poi)

            location_name = poi["name"]
            location_name = location_name if location_name else "<MISSING>"
            street_address = poi["address"]["streetAddress"]
            street_address = street_address if street_address else "<MISSING>"
            city = poi["address"]["addressLocality"]
            city = city if city else "<MISSING>"
            state = poi["address"]["addressRegion"]
            state = state if state else "<MISSING>"
            zip_code = poi["address"]["postalCode"]
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = "<MISSING>"
            store_number = "<MISSING>"
            phone = poi.get("telephone")
            phone = phone if phone else "<MISSING>"
            location_type = poi["@type"]
            location_type = location_type if location_type else "<MISSING>"
            geo = loc_dom.xpath('//a[contains(@href, "/@")]/@href')
            latitude = ""
            longitude = ""
            if geo:
                geo = geo[-1].split("/@")[-1].split(",")[:2]
                latitude = geo[0]
                longitude = geo[1]
            hoo = loc_dom.xpath('//li[span[@class="hours_HoursDay__D_ako"]]//text()')
            hoo = [elem.strip() for elem in hoo if elem.strip()]
            hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

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
                country_code=country_code,
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
