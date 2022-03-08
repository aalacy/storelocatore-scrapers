from lxml import etree
from time import sleep

from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgFirefox
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    start_url = "https://www.cinnabon.uk/stores"
    domain = "cinnabon.uk"
    with SgFirefox() as driver:
        driver.get(start_url)
        sleep(10)
        driver.switch_to.frame(driver.find_element_by_name("htmlComp-iframe"))
        dom = etree.HTML(driver.page_source)

    all_locations = dom.xpath('//div[@class="storelocator-store"]')
    for poi_html in all_locations:
        location_name = poi_html.xpath(
            './/a[@class="storelocator-viewlink storelocator-storename"]/text()'
        )[0]

        raw_addr = poi_html.xpath('.//p[@class="storelocator-address"]/text()')
        raw_addr = " ".join([e.strip() for e in raw_addr if e.strip()])
        addr = parse_address_intl(raw_addr)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += ", " + addr.street_address_2
        phone = poi_html.xpath('.//a[contains(@href, "tel")]/text()')
        phone = phone[0] if phone else ""
        hoo = poi_html.xpath('.//p[@class="storelocator-opening-daily "]//text()')
        hoo = " ".join([e.strip() for e in hoo])

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=street_address,
            city=addr.city,
            state="",
            zip_postal=addr.postcode,
            country_code="",
            store_number="",
            phone=phone,
            location_type="",
            latitude="",
            longitude="",
            hours_of_operation=hoo,
            raw_address=raw_addr,
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
