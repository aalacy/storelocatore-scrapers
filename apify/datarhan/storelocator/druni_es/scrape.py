# -*- coding: utf-8 -*-
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.druni.es/perfumerias"
    domain = "druni.es"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@id="modal-store"]')
    next_page = dom.xpath('//a[@title="Siguiente"]/@href')
    while next_page:
        response = session.get(next_page[0])
        dom = etree.HTML(response.text)
        all_locations += dom.xpath('//div[@id="modal-store"]')
        next_page = dom.xpath('//a[@title="Siguiente"]/@href')

    for poi_html in all_locations:
        location_name = poi_html.xpath('.//p[@class="data-title"]/text()')[0]
        street_address = poi_html.xpath('.//span[@class="data-street"]/text()')[0]
        raw_data = poi_html.xpath('.//span[@class="data-address"]/text()')[:2]
        phone = poi_html.xpath('.//span[@class="data-phone"]/a/text()')[0]
        geo = (
            poi_html.xpath('.//a[contains(text(), "Ver en google maps")]/@href')[0]
            .split("=")[-1]
            .split(",")
        )
        hoo = poi_html.xpath('.//div[@class="time-table"]/text()')
        hoo = " ".join(hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=street_address,
            city=raw_data[0].split(", ")[0],
            state="",
            zip_postal=raw_data[0].split(", ")[1],
            country_code="España",
            store_number="",
            phone=phone,
            location_type=location_name.split("-")[0],
            latitude=geo[0],
            longitude=geo[1],
            hours_of_operation=hoo,
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
