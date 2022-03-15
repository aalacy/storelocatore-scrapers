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

    start_url = "https://www.converse.com.ar/encontrar-un-local/"
    domain = "converse.com.ar"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//div[@class="su-column-inner su-u-clearfix su-u-trim" and h3]'
    )
    for poi_html in all_locations:
        location_name = poi_html.xpath(".//h3/text()")[0]
        raw_data = poi_html.xpath(".//p/text()")
        raw_data = [e.strip() for e in raw_data if e.strip()]
        hoo = " ".join([e for e in raw_data if "hs." in e])
        raw_address = ", ".join([e for e in raw_data if "hs." not in e][:-1])
        addr = parse_address_intl(raw_address)
        street_address = raw_address.replace(", Buenos Aires", "")

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=street_address,
            city=addr.city,
            state="",
            zip_postal=addr.postcode,
            country_code="AR",
            store_number="",
            phone=raw_data[-1],
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
