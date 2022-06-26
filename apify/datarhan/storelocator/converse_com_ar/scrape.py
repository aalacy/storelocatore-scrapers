# -*- coding: utf-8 -*-
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://backend.converse.com.ar/shop-api/minorista/stores"
    domain = "converse.com.ar"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    all_locations = session.get(start_url, headers=hdr).json()
    for poi in all_locations:
        if not poi["address"]:
            continue

        raw_data = etree.HTML(poi["note"]).xpath("//text()")
        raw_data = [e.strip() for e in raw_data if e.strip()]
        hoo = [e for e in raw_data if "hs" in e]
        hoo = " ".join(hoo)
        phone = [e for e in raw_data if len(e.split("-")) == 3][0]
        city = raw_data[0]
        if len(city.split("-")) == 3:
            city = ""
        hoo = etree.HTML(poi["note"]).xpath("//text()")[-1].strip()
        if hoo.startswith("Viernes"):
            hoo = etree.HTML(poi["note"]).xpath("//text()")[-2:]
            hoo = [e.strip() for e in hoo if e.strip()]
            hoo = " ".join(hoo).strip()

        item = SgRecord(
            locator_domain=domain,
            page_url="https://converse.com.ar/stores",
            location_name=poi["name"],
            street_address=poi["address"],
            city=city,
            state=poi["province"]["name"],
            zip_postal="",
            country_code="AR",
            store_number=poi["code"],
            phone=phone,
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
