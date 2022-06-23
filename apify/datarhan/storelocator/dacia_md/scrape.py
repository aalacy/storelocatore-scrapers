# -*- coding: utf-8 -*-
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://dacia.md/contacte/dealer.html"
    domain = "dacia.md"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//table[@id="DealersTable"]/tbody/tr')
    for poi_html in all_locations:
        location_name = poi_html.xpath(
            './/span[@class="dealers-list_arrowlink-text"]/text()'
        )[0].replace("Vezi pe harta", "")
        raw_address = (
            poi_html.xpath('.//a[@class="dealers-list_arrowlink"]/following::text()')[0]
            .strip()
            .split()
        )
        phone = poi_html.xpath('.//a[contains(@href, "tel")]/text()')[0].split(":")[-1]
        location_type = poi_html.xpath(
            './/span[@class="dealers-list_legend-item-ico"]/@title'
        )
        location_type = ", ".join([e.strip() for e in location_type])

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=" ".join(raw_address[2:]),
            city=raw_address[0],
            state="",
            zip_postal=raw_address[1],
            country_code="MD",
            store_number="",
            phone=phone,
            location_type=location_type,
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
