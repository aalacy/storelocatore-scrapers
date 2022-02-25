import ssl
from lxml import etree
from time import sleep
import tenacity

from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgChrome
from sgpostal.sgpostal import parse_address_intl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context


@tenacity.retry(wait=tenacity.wait_fixed(3))
def get_with_retry(driver, url):
    driver.get(url)
    sleep(30)
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
            location_name = poi_html.xpath(".//h2/text()")[0]
            raw_data = loc_dom.xpath('//div[@class="global__map-showroom"]//p/text()')
            addr = parse_address_intl(raw_data[0])
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += ", " + addr.street_address_2

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=addr.city,
                state="",
                zip_postal=addr.postcode,
                country_code="RO",
                store_number="",
                phone=raw_data[1].split("/")[0],
                location_type="",
                latitude="",
                longitude="",
                hours_of_operation=raw_data[2],
                raw_address=raw_data[0],
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
