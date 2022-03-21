# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.converse.co.kr/converse/store_data.js"
    domain = "converse.co.kr"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    all_locations = session.get(start_url, headers=hdr).json()
    for poi in all_locations:
        street_address = poi["address1"]
        if poi["address2"]:
            street_address += ", " + poi["address2"]

        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.converse.co.kr/store.html",
            location_name=poi["store_name"],
            street_address=street_address,
            city=poi["city"],
            state=poi["region"],
            zip_postal=poi["zipcode"],
            country_code="KR",
            store_number=poi["id"],
            phone=poi["store_tel"],
            location_type=poi["store_type"],
            latitude=poi["latitude"],
            longitude=poi["longitude"],
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
