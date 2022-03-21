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

    start_url = "https://www.phonehouse.es/tiendas/phonehouse.html"
    domain = "phonehouse.es"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    all_regions = dom.xpath('//ul[@id="listado-tiendas-columnas"]/li/a/@href')
    for url in all_regions:
        if url == "/tiendas/.html":
            continue
        url = urljoin(start_url, url)
        response = session.get(url)
        dom = etree.HTML(response.text)

        all_locations = dom.xpath('//ul[@class="tiendas"]/li/a/@href')
        for url in all_locations:
            page_url = urljoin(start_url, url)
            loc_response = session.get(page_url)
            loc_dom = etree.HTML(loc_response.text)

            location_name = loc_dom.xpath("//h1/text()")[0]
            raw_address = loc_dom.xpath('//li[span[@class="icon-tiendas"]]/text()')[0]
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += ", " + addr.street_address_2
            if street_address and street_address.isnumeric():
                street_address = raw_address.split(", ")[0]
            phone = loc_dom.xpath('//li/span[@class="pc"]/text()')
            phone = phone[0] if phone else ""
            if phone and phone == "-":
                phone = ""
            geo = (
                loc_dom.xpath("//iframe/@src")[-1]
                .split("!2d")[-1]
                .split("!3m2")[0]
                .split("!3d")
            )
            zip_code = addr.postcode
            if zip_code:
                zip_code = zip_code.split()[0]
            hoo = loc_dom.xpath('//li[span[@class="icon-horario"]]/text()')
            hoo = hoo[0] if hoo else ""
            if hoo and hoo.startswith("."):
                hoo = hoo[1:]

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=zip_code,
                country_code="ES",
                store_number="",
                phone=phone,
                location_type="",
                latitude=geo[1].split("!")[0],
                longitude=geo[0],
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
