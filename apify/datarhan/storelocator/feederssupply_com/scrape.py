from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl
from sgselenium.sgselenium import SgFirefox


def fetch_data():
    session = SgRequests()
    domain = "feederssupply.com"
    start_url = "https://www.feederssupply.com/store-locator"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//a[contains(text(), "Details")]/@href')
    with SgFirefox() as driver:
        for page_url in all_locations:
            driver.get(page_url)
            loc_dom = etree.HTML(driver.page_source)

            location_name = loc_dom.xpath(
                '//div[@class="cs-storeInnerTextHldr"]/h4/text()'
            )[0]
            raw_data = loc_dom.xpath('//div[@class="cs-storeInnerTextHldr"]/p/text()')
            addr = parse_address_intl(raw_data[0])
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += ", " + addr.street_address_2
            geo = (
                loc_dom.xpath('//div[@class="cs-storeInner-top"]//iframe/@src')[0]
                .split("!2d")[-1]
                .split("!2m")[0]
                .split("!3d")
            )
            hoo = loc_dom.xpath(
                '//li[b[contains(text(), "Store Hours:")]]/following-sibling::li/text()'
            )
            hoo = " ".join(hoo)

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code=addr.country,
                store_number="",
                phone=raw_data[-1],
                location_type="",
                latitude=geo[1],
                longitude=geo[0],
                hours_of_operation=hoo,
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
