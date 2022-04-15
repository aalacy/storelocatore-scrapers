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

    start_url = "https://www.josimar.com.ar/institucional/sucursales?sc=8"
    domain = "josimar.com.ar"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@id="stores"]/div/text()')
    for poi in all_locations:
        poi = json.loads(poi)
        poi = list(poi.values())[0]
        city = "Buenos Aires"

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=poi["name"],
            street_address=poi["address"],
            city=city,
            state="",
            zip_postal="",
            country_code="AR",
            store_number="",
            phone=poi["phone"],
            location_type="",
            latitude="",
            longitude="",
            hours_of_operation=poi["timetable"],
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
