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

    start_url = "https://www.brownthomas.com/"
    domain = "brownthomas.com"

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="header-store"]/div/a/@href')
    for page_url in all_locations:
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        raw_data = loc_dom.xpath('//div[h4[contains(text(), "Store Details")]]/text()')
        raw_data = [e.strip() for e in raw_data if e.strip()]
        raw_address = ", ".join(raw_data[1:])
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        store_number = ""
        if "StoreID=" in page_url:
            store_number = page_url.split("=")[-1]
        phone = loc_dom.xpath('//div[h4[contains(text(), "Store Queries")]]/text()')
        phone = [e.strip() for e in phone if "+" in e]
        phone = phone[0] if phone else ""

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=raw_data[0],
            street_address=street_address,
            city=addr.city,
            state=addr.state,
            zip_postal=addr.postcode,
            country_code=addr.country,
            store_number=store_number,
            phone=phone,
            location_type="",
            latitude="",
            longitude="",
            hours_of_operation="",
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
