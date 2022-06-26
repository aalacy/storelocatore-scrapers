# -*- coding: utf-8 -*-
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "http://t-grill.com/locations"
    domain = "t-grill.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//*[@data-ux="ContentText"]')
    for poi_html in all_locations:
        raw_data = poi_html.xpath(".//text()")
        raw_data = [e.strip() for e in raw_data]

        raw_address = raw_data[0]
        if "now open" in raw_address.lower():
            raw_address = raw_data[1]
        city = raw_address.split(", ")[0]
        state = raw_address.split(",")[1].split()[0].strip()
        street_address = " ".join(raw_address.split(",")[1].split()[1:])

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name="",
            street_address=street_address,
            city=city,
            state=state,
            zip_postal="",
            country_code="",
            store_number="",
            phone=raw_data[-1],
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
