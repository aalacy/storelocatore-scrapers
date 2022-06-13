# -*- coding: utf-8 -*-
import yaml
from yaml import FullLoader
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.coviran.pt/localizador"
    domain = "coviran.pt"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    data = (
        dom.xpath('//script[contains(text(), "places")]/text()')[0]
        .split("places:")[-1]
        .replace("\r\n", "")
    )
    all_locations = yaml.load(data.split(",            icon:")[0], Loader=FullLoader)

    for poi in all_locations:
        raw_address = etree.HTML(poi["address"]).xpath("//text()")
        raw_address = [e.strip() for e in raw_address]

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=poi["title"],
            street_address=raw_address[0],
            city=raw_address[1],
            state="",
            zip_postal="",
            country_code="PT",
            store_number="",
            phone=poi["phone"],
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
