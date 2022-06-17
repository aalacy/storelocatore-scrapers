# -*- coding: utf-8 -*-
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
        item = SgRecord(
            locator_domain=domain,
            page_url="https://converse.com.ar/stores",
            location_name=poi["name"],
            street_address=poi["address"],
            city="",
            state=poi["province"]["name"],
            zip_postal="",
            country_code="AR",
            store_number=poi["code"],
            phone=poi["phone"],
            location_type="",
            latitude="",
            longitude="",
            hours_of_operation="",
            raw_address="",
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
