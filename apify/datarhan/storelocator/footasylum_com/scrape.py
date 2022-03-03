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

    start_url = "https://www.footasylum.com/page/storelocator/"
    domain = "footasylum.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    data = dom.xpath('//script[contains(text(), "myStores = ")]/text()')[0].split(
        "myStores ="
    )[-1][:-1]
    data = json.loads(data)

    for poi in data["stores"]:
        street_address = poi["address1"]
        if poi["address2"]:
            street_address += ", " + poi["address2"]
        if poi["address3"]:
            street_address += ", " + poi["address3"]

        item = SgRecord(
            locator_domain=domain,
            page_url=poi["storeLink"],
            location_name=poi["name"],
            street_address=street_address,
            city=poi["town"],
            state=poi["county"],
            zip_postal=poi["postcode"],
            country_code=poi["country"],
            store_number=poi["storenumber"],
            phone=poi["storecontacts"],
            location_type="",
            latitude=poi["pca_wgs84_latitude"],
            longitude=poi["pca_wgs84_longitude"],
            hours_of_operation=poi["openinghours"],
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
