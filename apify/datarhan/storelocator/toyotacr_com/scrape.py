from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "https://www.toyotacr.com/sucursales/"
    domain = "toyotacr.com"
    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//li[contains(@data-service, "nuevos")]')
    for poi_html in all_locations:
        location_name = poi_html.xpath(".//button/text()")[0]
        raw_address = poi_html.xpath(
            './/p[strong[contains(text(), "Dirección:")]]/following-sibling::p[1]/text()'
        )[0]
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += ", " + addr.street_address_2
        phone = poi_html.xpath(
            './/p[strong[contains(text(), "Teléfono:")]]/following-sibling::p[1]/text()'
        )
        phone = phone[0] if phone else ""
        hoo = poi_html.xpath(
            './/p[strong[contains(text(), "Horario Vehículos Nuevos y Usados:")]]/following-sibling::p[1]/text()'
        )
        hoo = hoo[0] if hoo else ""
        latitude = poi_html.xpath(".//@data-lat")[0]
        longitude = poi_html.xpath(".//@data-long")[0]

        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.toyotacr.com/sucursales/",
            location_name=location_name,
            street_address=street_address,
            city="",
            state="",
            zip_postal=addr.postcode,
            country_code="CR",
            store_number="",
            phone=phone,
            location_type="",
            latitude=latitude,
            longitude=longitude,
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
