from time import sleep
from lxml import etree

from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgFirefox


def fetch_data():
    domain = "uscold.com"
    start_url = "https://www.uscold.com/facilitiesmap/"

    with SgFirefox() as driver:
        driver.get(start_url)
        sleep(15)
        dom = etree.HTML(driver.page_source)

    all_locations = dom.xpath("//tr[@mid]")
    for poi_html in all_locations:
        location_name = poi_html.xpath('.//td[contains(@class, "title")]/text()')[0]
        raw_address = poi_html.xpath('.//td[contains(@class, "address")]/text()')[
            0
        ].split(", ")
        phone = poi_html.xpath('.//td[@class="wpgmza_table_description"]/p/text()')
        phone = [e.strip() for e in phone if "P:" in e]
        phone = phone[0] if phone else ""

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=raw_address[0],
            city=raw_address[1],
            state=raw_address[-1].split()[0],
            zip_postal=raw_address[-1].split()[-1],
            country_code="",
            store_number="",
            phone=phone,
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
