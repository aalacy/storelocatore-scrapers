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

    start_url = "https://www.converse.pl/sklepy-stacjonarne"
    domain = "converse.pl"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//div[@class="converse-faq__accordion-content typography__body-1"]/strong'
    )
    for poi_html in all_locations:
        location_name = poi_html.xpath(".//text()")[0].strip()
        raw_data = poi_html.xpath("./following::text()")[:2]
        raw_data = [e.strip() for e in raw_data]
        addr = parse_address_intl(raw_data[0])
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += ", " + addr.street_address_2

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=street_address,
            city=addr.city,
            state="",
            zip_postal=addr.postcode,
            country_code="PL",
            store_number="",
            phone=raw_data[-1].split(":")[-1],
            location_type="",
            latitude="",
            longitude="",
            hours_of_operation="",
            raw_address=raw_data[0],
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
