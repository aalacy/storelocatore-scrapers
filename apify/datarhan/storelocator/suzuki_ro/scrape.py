import ssl
from lxml import etree
from time import sleep
import tenacity

from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgChrome

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context


@tenacity.retry(wait=tenacity.wait_fixed(3))
def get_with_retry(driver, url):
    driver.get(url)
    driver.implicitly_wait(30)
    return driver.page_source


def fetch_data():
    start_url = "https://suzuki.ro/gaseste-dealer/"
    domain = "suzuki.ro"
    with SgChrome() as driver:
        driver.get(start_url)
        sleep(10)
        dom = etree.HTML(driver.page_source)
        all_locations = dom.xpath("//a[h2]")
        for poi_html in all_locations:
            page_url = poi_html.xpath("@href")[0]

            response = get_with_retry(driver, page_url)
            loc_dom = etree.HTML(response)
            location_name = loc_dom.xpath("//h3/text()")[0]
            street_address = loc_dom.xpath(
                '//div[img[@alt="showroom_location"]]/following-sibling::div[1]/p/text()'
            )[0]
            city = poi_html.xpath(".//following-sibling::h3/text()")[0].split(", ")[0]
            phone = loc_dom.xpath(
                '//div[img[@alt="phone"]]/following-sibling::div[1]/p/text()'
            )[0]
            hoo = loc_dom.xpath(
                '//div[img[@alt="schedule"]]/following-sibling::div[1]/p/text()'
            )[0]

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state="",
                zip_postal="",
                country_code="RO",
                store_number="",
                phone=phone,
                location_type="",
                latitude="",
                longitude="",
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
