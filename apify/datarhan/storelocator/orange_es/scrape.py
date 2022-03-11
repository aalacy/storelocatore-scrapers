# -*- coding: utf-8 -*-
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "https://www.orange.es/tiendas"
    domain = "orange.es"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="result-store"]')
    for poi_html in all_locations:
        page_url = poi_html.xpath(".//a/@href")[0]
        page_url = urljoin(start_url, page_url)
        location_name = poi_html.xpath(".//a/@title")[0]
        raw_address = poi_html.xpath('.//p[@class="data address"]/text()')
        addr = parse_address_intl(" ".join(raw_address))
        city = addr.city
        state = addr.state
        phone = poi_html.xpath('.//p[@class="data telephone"]/text()')
        phone = phone[0].split("/")[0] if phone else ""
        geo = (
            poi_html.xpath(".//button/@onclick")[0]
            .split("centerMap(")[-1]
            .split(", ")[:2]
        )
        hoo = poi_html.xpath('.//p[@class="data schedule"]/text()')
        hoo = hoo[0] if hoo else ""
        location_type = ""
        if hoo == "Laborables: Cerrado definitivamente":
            hoo = ""
            location_type = "Cerrado definitivamente"

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=raw_address[0].split(",")[0].strip(),
            city=city,
            state=state,
            zip_postal=raw_address[1].split("-")[0].split("/")[0],
            country_code="ES",
            store_number="",
            phone=phone,
            location_type=location_type,
            latitude=geo[0],
            longitude=geo[1],
            hours_of_operation=hoo,
            raw_address=" ".join(raw_address),
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
