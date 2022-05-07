# -*- coding: utf-8 -*-
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.adecco.se/hitta-kontor/"
    domain = "adecco.se"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="content"]/ul/a/@href')
    for url in all_locations:
        page_url = urljoin(start_url, url)
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath("//h1/text()")[0]
        raw_data = loc_dom.xpath(
            '//label[contains(text(), "BESÖKSADRESS")]/following-sibling::p/text()'
        )
        if not raw_data:
            raw_data = loc_dom.xpath('//p[@class="new-FooterAdress"]/text()')
        raw_data = [e.strip() for e in raw_data if e.strip()]
        if "Adecco c/o BYN Växjö" in raw_data[0]:
            raw_data = raw_data[1:]
        phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')[0]
        geo = loc_dom.xpath("//iframe/@data-lazy")
        if geo:
            geo = geo[0].split("!2d")[-1].split("!2m")[0].split("!3d")
        else:
            geo = ["", ""]
        hoo = ""
        if len(raw_data) > 2:
            hoo = raw_data[2].split("Vardagar:")[-1]

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=raw_data[0],
            city=" ".join(raw_data[1].split()[2:]),
            state="",
            zip_postal=" ".join(raw_data[1].split()[:2]),
            country_code="SE",
            store_number="",
            phone=phone,
            location_type="",
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
