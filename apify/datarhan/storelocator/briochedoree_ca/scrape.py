# -*- coding: utf-8 -*-
import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://briochedoree.ca/nos-boutiques/"
    domain = "briochedoree.ca"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    data = (
        dom.xpath('//script[contains(text(), "mapMarkers")]/text()')[0]
        .split("Markers =")[-1]
        .split(" window.stored")[0]
        .strip()[:-1]
    )

    all_locations = json.loads(data)
    for poi in all_locations:
        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=poi["titre"],
            street_address=poi["rue"],
            city=poi["ville"],
            state=poi["province"],
            zip_postal=poi["codepostal"],
            country_code="CA",
            store_number=poi["id"],
            phone="",
            location_type="",
            latitude=poi["lat"],
            longitude=poi["lng"],
            hours_of_operation="",
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
