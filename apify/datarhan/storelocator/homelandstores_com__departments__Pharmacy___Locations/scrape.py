# -*- coding: utf-8 -*-
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.homelandstores.com/departments/Pharmacy_Locations"
    domain = "homelandstores.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//table[@class="table table-bordered table-striped"]/tbody/tr'
    )[1:]
    for poi_html in all_locations:
        raw_data = poi_html.xpath(".//td/text()")
        raw_data = [e.strip() for e in raw_data]
        hoo = f"Mon-Fri {raw_data[-3]}  Sat {raw_data[-2]} Sun {raw_data[-1]}"

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=raw_data[0],
            street_address=raw_data[1],
            city=raw_data[2],
            state=raw_data[3],
            zip_postal=raw_data[4],
            country_code="",
            store_number="",
            phone=raw_data[5],
            location_type="",
            latitude="",
            longitude="",
            hours_of_operation=hoo,
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
