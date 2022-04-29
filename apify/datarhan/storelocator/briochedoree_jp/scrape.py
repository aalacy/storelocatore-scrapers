# -*- coding: utf-8 -*-
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "http://www.briochedoree.jp/"
    domain = "briochedoree.jp"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="shopinfo"]')
    for poi_html in all_locations:
        location_name = " ".join(poi_html.xpath('.//p[@class="shopname fr"]//text()'))
        raw_data = poi_html.xpath('.//p[@class="shopaddress"]/text()')
        addr = parse_address_intl(raw_data[0])
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += ", " + addr.street_address_2

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=street_address,
            city=addr.city,
            state=addr.state,
            zip_postal=addr.postcode,
            country_code="JP",
            store_number="",
            phone=raw_data[1].split(":")[-1],
            location_type="",
            latitude="",
            longitude="",
            hours_of_operation="",
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
