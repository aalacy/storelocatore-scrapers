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

    start_url = "https://tonyromas.es/reservas/#"
    domain = "tonyromas.es"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_cities = dom.xpath(
        '//a[contains(text(), "ELEGIR CIUDAD")]/following-sibling::ul//a/@href'
    )
    for url in all_cities:
        page_url = urljoin(start_url, url)
        response = session.get(page_url)
        dom = etree.HTML(response.text)
        all_locations = dom.xpath(
            '//div[div[div[h5[span[contains(text(), "Tony Roma")]]]]]'
        )
        all_locations += dom.xpath('//div[div[div[h5[contains(text(), "Tony Roma")]]]]')
        for poi_html in all_locations:
            location_name = poi_html.xpath(".//h5//text()")[0]
            city = dom.xpath('//a[@aria-current="page"]/text()')[0]
            raw_address = poi_html.xpath(".//h5/following-sibling::*[1]//text()")[0]
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            zip_code = addr.postcode
            if zip_code:
                zip_code = zip_code.split("-")[0]
            phone = poi_html.xpath('.//a[contains(@href, "tel")]/text()')
            phone = phone[0] if phone else ""
            hoo = poi_html.xpath(
                './/div[div[p[strong[contains(text(), "Horarios:")]]]]/following-sibling::div[1]//text()'
            )
            hoo = " ".join([e.strip() for e in hoo if e.strip()])

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state="",
                zip_postal=zip_code,
                country_code="ES",
                store_number="",
                phone=phone,
                location_type="",
                latitude="",
                longitude="",
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
