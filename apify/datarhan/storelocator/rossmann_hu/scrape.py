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

    start_url = "https://shop.rossmann.hu/uzletkereso/"
    domain = "rossmann.hu"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    data = dom.xpath('//script[@id="__NEXT_DATA__"]/text()')[0]
    data = json.loads(data)
    for poi in data["props"]["pageProps"]["stores"]:
        hoo = poi["openings"].replace("\n", " ").strip()
        if hoo.endswith(":"):
            hoo += " closed"

        item = SgRecord(
            locator_domain=domain,
            page_url="https://shop.rossmann.hu/uzletkereso/",
            location_name=poi["name"],
            street_address=poi["street"],
            city=poi["city"],
            state="",
            zip_postal=poi["zip_code"],
            country_code="",
            store_number=poi["id"],
            phone="",
            location_type="",
            latitude=poi["lat"],
            longitude=poi["lng"],
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
