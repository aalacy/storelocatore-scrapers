from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = (
        "https://www.suzukipan.com/suzuki/site/edic/base/port/concesionarios.html"
    )
    domain = "suzukipan.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//ul[@class="list listresults"]/li')
    for poi_html in all_locations:
        location_name = poi_html.xpath('.//p[@class="tit"]/text()')[0]
        raw_address = poi_html.xpath(".//p/span/text()")[0].strip()
        if raw_address.endswith("."):
            raw_address = raw_address[:-1]
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += ", " + addr.street_address_2
        latitude = poi_html.xpath("@data-latitud")[0]
        longitude = poi_html.xpath("@data-longitud")[0]
        if poi_html.xpath("@data-venta")[0] != "si":
            continue
        phone = poi_html.xpath('.//a[contains(@href, "tel")]/text()')[0]
        hoo = poi_html.xpath(
            './/p[contains(text(), "Horario de Ventas")]/following-sibling::p[1]//text()'
        )
        if not hoo:
            hoo = poi_html.xpath(
                './/p[span[contains(text(), "Horario de Ventas")]]/following-sibling::p[1]//text()'
            )
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
