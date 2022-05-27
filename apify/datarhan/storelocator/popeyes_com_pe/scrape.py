from lxml import etree
from time import sleep

from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgFirefox
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    start_url = "https://www.popeyes.com.pe/locales"
    domain = "popeyes.com.pe"

    with SgFirefox() as driver:
        driver.get(start_url)
        sleep(5)
        dom = etree.HTML(driver.page_source)

    all_locations = dom.xpath('//div[@class="store-card"]')
    for poi_html in all_locations:
        location_name = poi_html.xpath('.//div[@class="store-name"]/p/text()')[0]
        raw_address = poi_html.xpath('.//div[@class="store-address"]/p/text()')[0]
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += ", " + addr.street_address_2
        phone = poi_html.xpath('.//div[@class="store-info-phone"]/span/text()')[0]
        if phone == "-":
            phone = ""
        hoo = poi_html.xpath('.//div[@class="text-time"]//li/text()')
        hoo = [e.split("Salón:")[-1].strip() for e in hoo if "Salón" in e][0]

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=street_address,
            city=addr.city,
            state=addr.state,
            zip_postal=addr.postcode,
            country_code="",
            store_number="",
            phone=phone,
            location_type="",
            latitude="",
            longitude="",
            hours_of_operation=hoo,
            raw_address=raw_address,
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
