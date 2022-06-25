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

    start_url = "http://adeccopr.com/sucursales/"
    domain = "adeccopr.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//div[@class="vc_btn3-container vc_btn3-center"]/a/@href'
    )
    for page_url in all_locations:
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath("//h1/text()")[-1]
        phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')[0]
        raw_address = loc_dom.xpath(
            '//h6[contains(text(), "Dirección")]/following-sibling::div[1]//text()'
        )
        raw_address = " ".join([e.strip() for e in raw_address if e.strip()])
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        hoo = loc_dom.xpath(
            '//h6[contains(text(), "Horario")]/following-sibling::div[1]//text()'
        )
        hoo = " ".join([e.strip() for e in hoo if e.strip()])
        geo = (
            loc_dom.xpath("//iframe/@src")[0]
            .split("!2d")[-1]
            .split("!3m")[0]
            .split("!3d")
        )
        zip_code = addr.postcode
        if zip_code:
            zip_code = zip_code.replace("P.R. ", "")

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=addr.city,
            state=addr.state,
            zip_postal=zip_code,
            country_code="PR",
            store_number="",
            phone=phone,
            location_type="",
            latitude=geo[0].split("!")[0],
            longitude=geo[1].split("!")[0],
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
