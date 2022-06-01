# -*- coding: utf-8 -*-
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://www.adecco.gr/%CE%B2%CF%81%CE%B5%CF%82-%CF%85%CF%80%CE%BF%CE%BA%CE%B1%CF%84%CE%AC%CF%83%CF%84%CE%B7%CE%BC%CE%B1-%CE%BA%CE%BF%CE%BD%CF%84%CE%AC-%CF%83%CE%BF%CF%85/"
    domain = "adecco.gr"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="toggles accordion"]')
    for poi_html in all_locations:
        location_name = poi_html.xpath(".//h3/a/text()")[0]
        raw_address = poi_html.xpath('.//div[@class="wpb_wrapper"]/p[1]/text()')[
            0
        ].split(", ")
        phone = poi_html.xpath('.//div[@class="wpb_wrapper"]/p[2]/text()')[0]

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=raw_address[0],
            city=raw_address[2],
            state="",
            zip_postal=raw_address[1].replace("Τ.Κ.", "").replace("T.K.", ""),
            country_code="GR",
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
