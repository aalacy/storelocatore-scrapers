# -*- coding: utf-8 -*-
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "http://www.grupolideronline.com.br/supermercado"
    domain = "grupolideronline.com.br"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//div[@class="section-heading title-style5"]/following-sibling::div[2]/div'
    )
    for poi_html in all_locations:
        location_name = poi_html.xpath(".//div/span/text()")[0].strip()
        raw_data = poi_html.xpath('.//div/p[@class="no-margin"]/text()')
        raw_data = [e.strip() for e in raw_data if e.strip()]
        raw_data = [e.strip() for e in raw_data if e.strip()]

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=raw_data[0],
            city="",
            state="",
            zip_postal="",
            country_code="BR",
            store_number="",
            phone=raw_data[1].split(":")[-1],
            location_type="",
            latitude="",
            longitude="",
            hours_of_operation=raw_data[2].split("Horário:")[-1],
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
