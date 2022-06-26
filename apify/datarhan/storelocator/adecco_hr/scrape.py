# -*- coding: utf-8 -*-
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://www.adecco.hr/poslovnice/"
    domain = "adecco.hr"

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[h3[@class="text-red"]]')
    for poi_html in all_locations:
        location_name = poi_html.xpath(".//h3/text()")[0]
        raw_data = poi_html.xpath('.//p[@class="text-black text-20"]/text()')[0].split(
            ","
        )
        phone = poi_html.xpath('.//a[contains(@href, "tel")]//p/text()')
        phone = phone[0] if phone else ""
        zip_code = raw_data[1].split()[0]
        geo = (
            dom.xpath(f'//iframe[contains(@src, "{zip_code}")]/@src')[0]
            .split("!2d")[1]
            .split("!3m")[0]
            .split("!3d")
        )

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=raw_data[0],
            city=" ".join(raw_data[1].split()[1:]),
            state="",
            zip_postal=zip_code,
            country_code="HR",
            store_number="",
            phone=phone,
            location_type="",
            latitude=geo[1].split("!")[0],
            longitude=geo[0],
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
