# -*- coding: utf-8 -*-
# --extra-index-url https://dl.cloudsmith.io/KVaWma76J5VNwrOm/crawl/crawl/python/simple/
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "http://masapps.gritcreative.co/api/locations?key=2XTg2q524wA6bPgAV8Yjg97nfOimVmnL"
    domain = "maxfuel.net"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    data = session.get(start_url, headers=hdr).json()
    for store_number, poi in data.items():
        item = SgRecord(
            locator_domain=domain,
            page_url="http://maxfuel.net/locations/#/",
            location_name=poi["name"],
            street_address=poi["address"],
            city=poi["city"],
            state=poi["state"],
            zip_postal=poi["zip"],
            country_code="",
            store_number=store_number,
            phone=poi["phone"],
            location_type="",
            latitude=poi["lat"],
            longitude=poi["lng"],
            hours_of_operation=poi["hours"],
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
