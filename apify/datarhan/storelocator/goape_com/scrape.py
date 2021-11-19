import ssl
from lxml import etree

from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl
from sgselenium.sgselenium import SgChrome

ssl._create_default_https_context = ssl._create_unverified_context


def fetch_data():
    user_agent = "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1"
    start_url = "https://www.goape.com/locations/"
    domain = "goape.com"

    with SgChrome(user_agent=user_agent) as driver:
        driver.get(start_url)
        driver.implicitly_wait(30)
        dom = etree.HTML(driver.page_source)

        all_locations = dom.xpath('//a[contains(text(), "Visit Location")]/@href')
        for page_url in all_locations:
            driver.get(page_url)
            loc_dom = etree.HTML(driver.page_source)

            location_name = loc_dom.xpath(
                '//p[@class="location-subtitle desktop-only"]/text()'
            )[0].replace(" - ", "")
            raw_address = loc_dom.xpath(
                '//p[@class="location-subtitle desktop-only"]/a/text()'
            )[0]
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="",
                store_number="",
                phone="",
                location_type="",
                latitude="",
                longitude="",
                hours_of_operation="",
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
