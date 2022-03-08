# -*- coding: utf-8 -*-
import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()
    start_url = "http://www.intersport.cn/Shop.html"
    domain = "intersport.cn"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    data = (
        dom.xpath('//script[contains(text(), "var data")]/text()')[0]
        .split("var data = ")[-1]
        .split(";\n        console")[0]
    )
    data = json.loads(data)

    for poi in data["arr"]:
        raw_address = poi["detailAddress"]
        addr = parse_address_intl(raw_address)

        item = SgRecord(
            locator_domain=domain,
            page_url="http://www.intersport.cn/Shop.html",
            location_name=poi["companyName"],
            street_address=poi["address"],
            city=addr.city,
            state="",
            zip_postal=poi["zipCode"],
            country_code="CN",
            store_number=poi["id"],
            phone="",
            location_type="",
            latitude=poi["lat"],
            longitude=poi["lng"],
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
