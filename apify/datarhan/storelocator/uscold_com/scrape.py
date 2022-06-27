from time import sleep
from lxml import etree

from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgFirefox
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    domain = "uscold.com"
    start_url = "https://www.uscold.com/facilitiesmap/"

    with SgFirefox() as driver:
        driver.get(start_url)
        sleep(25)
        dom = etree.HTML(driver.page_source)

    all_locations = dom.xpath("//tr[@mid]")
    for poi_html in all_locations:
        location_name = poi_html.xpath('.//td[contains(@class, "title")]/text()')[0]
        raw_address = poi_html.xpath('.//td[contains(@class, "address")]/text()')[0]
        data = poi_html.xpath('.//td[@class="wpgmza_table_description"]/p/text()')
        phone = [e.strip() for e in data if "p:" in e.lower()]
        if not phone:
            phone = [e.strip() for e in data if "tel:" in e.lower()]
        phone = (
            phone[0].split("P:")[-1].split("p:")[-1].split("Tel:")[-1] if phone else ""
        )
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += ", " + addr.street_address_2
        city = addr.city
        if city == "Park":
            city = "McClellan Park"

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=addr.state,
            zip_postal=addr.postcode,
            country_code="",
            store_number="",
            phone=phone,
            location_type="",
            latitude="",
            longitude="",
            hours_of_operation="",
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
