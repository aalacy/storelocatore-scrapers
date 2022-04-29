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

    start_url = "https://www.napolipizza.jp/store/"
    domain = "napolipizza.jp"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_cities = dom.xpath('//table[@class="area_box"]//li/a/@href')
    for url in all_cities:
        response = session.get(url)
        dom = etree.HTML(response.text)
        all_locations = dom.xpath(
            '//a[contains(@href, "https://www.napolipizza.jp/store/")]/@href'
        )
        for page_url in all_locations:
            if page_url == "https://www.napolipizza.jp/store/":
                continue
            loc_response = session.get(page_url)
            loc_dom = etree.HTML(loc_response.text)

            location_name = loc_dom.xpath("//td/h1/text()")[0]
            phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')
            phone = phone[0] if phone else ""
            raw_address = loc_dom.xpath(
                '//th[contains(text(), "住所")]/following-sibling::td[1]//text()'
            )
            raw_address = " ".join(
                " ".join([e.strip() for e in raw_address if e.strip()]).split()
            )
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            geo = (
                loc_dom.xpath("//iframe/@src")[0]
                .split("!2d")[1]
                .split("!3m")[0]
                .split("!3d")
            )
            hoo = loc_dom.xpath(
                '//th[contains(text(), "営業時間")]/following-sibling::td[1]//text()'
            )
            hoo = " ".join([e.strip() for e in hoo if e.strip()])

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="JP",
                store_number=page_url.split("/")[-2],
                phone=phone,
                location_type="",
                latitude=geo[1].split("!")[0],
                longitude=geo[0].split("!")[0],
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
