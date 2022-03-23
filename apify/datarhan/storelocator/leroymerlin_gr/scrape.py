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

    start_url = "https://www.leroymerlin.gr/gr/stores"
    domain = "leroymerlin.gr"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//a[@class="storesButtonLink"]/@href')
    for page_url in all_locations:
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath("//h1/text()")[0]
        raw_address = loc_dom.xpath('//div[@class="storeAdress col-12 px-0"]/text()')[
            0
        ].strip()
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += ", " + addr.street_address_2
        phone = (
            loc_dom.xpath('//div[@class="storeTel col-12 px-0"]/text()')[0]
            .strip()
            .split(":")[-1]
        )
        geo = (
            loc_dom.xpath('//div[@class="storeMap col-12 my-3"]/a/@href')[0]
            .split("/@")[-1]
            .split(",")[:2]
        )
        hoo = loc_dom.xpath('//div[h5[span[contains(text(), "Ωράριο")]]]//text()')
        hoo = [e.strip() for e in hoo if e.strip()][1:]
        hoo = " ".join(hoo)
        if not hoo:
            hoo = loc_dom.xpath(
                '//h3[span[contains(text(), "Ωράριο")]]/following-sibling::h5[1]//text()'
            )
            hoo = " ".join([e.strip() for e in hoo])
        if not hoo:
            hoo = loc_dom.xpath(
                '//h3[span[contains(text(), "Ωράριο")]]/following::text()'
            )
            hoo = " ".join([e.strip() for e in hoo if e.strip()])
        hoo = hoo.split("Τμήμα")[0]

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=addr.city,
            state=addr.state,
            zip_postal=addr.postcode,
            country_code="GR",
            store_number=page_url.split("=")[-1],
            phone=phone,
            location_type="",
            latitude=geo[0],
            longitude=geo[1],
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