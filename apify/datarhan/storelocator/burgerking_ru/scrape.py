import json
from lxml import etree

from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium import SgFirefox
from sgselenium.sgselenium import SgFirefox
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    start_url = "https://burgerkingrus.ru/api-web-front/middleware/restaurants/search"
    domain = "burgerking.ru"

    with SgFirefox() as driver:
        driver.get(start_url)
        dom = etree.HTML(driver.page_source)
    data = json.loads(dom.xpath('//div[@id="json"]/text()')[0])

    for poi in data["items"]:
        addr = parse_address_intl(poi["name"])
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2

        item = SgRecord(
            locator_domain=domain,
            page_url="https://burgerkingrus.ru/restaurants",
            location_name=poi["name"],
            street_address=street_address,
            city=addr.city,
            state="",
            zip_postal="",
            country_code="",
            store_number=poi["id"],
            phone=poi["phone"],
            location_type="",
            latitude=poi["latitude"],
            longitude=poi["longitude"],
            hours_of_operation="",
            raw_address=poi["name"],
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
