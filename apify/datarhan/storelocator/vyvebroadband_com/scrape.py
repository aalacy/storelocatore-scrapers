# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://vyvebroadband.com/api/payment-centers/"
    domain = "vyvebroadband.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    data = session.get(start_url, headers=hdr).json()
    for poi in data["local_offices"]:

        item = SgRecord(
            locator_domain=domain,
            page_url="https://vyvebroadband.com/payment-centers/",
            location_name=poi["address1"],
            street_address=poi["address2"],
            city=poi["city"],
            state=poi["state"],
            zip_postal=poi["zipcode"],
            country_code="",
            store_number=poi["id"],
            phone="",
            location_type="",
            latitude="",
            longitude="",
            hours_of_operation=poi["hours1"],
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
