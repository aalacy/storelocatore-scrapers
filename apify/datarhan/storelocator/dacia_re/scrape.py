# -*- coding: utf-8 -*-
from lxml import etree
from sgpostal.sgpostal import parse_address_intl

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://dacia.re/nos-concessions/"
    domain = "dacia.re"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="et_pb_tab_content"]')
    for poi_html in all_locations:
        location_name = poi_html.xpath(".//h2/text()")[0]
        raw_address = poi_html.xpath(".//h4/text()")[0]
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        phone = poi_html.xpath(".//h5/text()")[0].split(":")[-1]
        hoo = poi_html.xpath(".//p/span//text()")[2:]
        hoo = " ".join([e.strip() for e in hoo if e.strip()])
        if not hoo:
            hoo = poi_html.xpath(".//p/span//text()")[1].split("ouverte du")[1][:-1]
        geo = (
            poi_html.xpath(".//iframe/@data-src")[0]
            .split("!2d")[1]
            .split("!2m")[0]
            .split("!3d")
        )

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=street_address,
            city=addr.city,
            state="",
            zip_postal=addr.postcode,
            country_code="RE",
            store_number="",
            phone=phone,
            location_type="",
            latitude=geo[1],
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
