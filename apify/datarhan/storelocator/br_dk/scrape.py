# -*- coding: utf-8 -*-
# --extra-index-url https://dl.cloudsmith.io/KVaWma76J5VNwrOm/crawl/crawl/python/simple/
from datetime import datetime

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://api.sallinggroup.com/v2/stores/?brand=br&per_page=200"
    domain = "br.dk"
    hdr = {
        "accept": "application/json, text/plain, */*",
        "authorization": "Bearer 4a368f3b-2d01-4338-bc9f-2b5c7d81d195",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36",
    }
    all_locations = session.get(start_url, headers=hdr).json()
    for poi in all_locations:
        sn = poi["name"].lower().replace(" ", "-")
        if poi["name"] == "BR Frederiksberg":
            sn = "br-frederiksberg-centret"
        hoo = []
        for e in poi["hours"]:
            if e["closed"]:
                closes_time = datetime.fromisoformat(str(e["date"]))
                closes = closes_time.strftime("%A %d %b, %Y")
                hoo.append(f"{closes} closed")
            else:
                opens_time = datetime.fromisoformat(str(e["open"]))
                opens = opens_time.strftime("%A %d %b, %Y, %H:%M:%S")
                closes_time = datetime.fromisoformat(str(e["close"]))
                closes = closes_time.strftime("%H:%M:%S")
                hoo.append(f"{opens} - {closes}")
        hoo = " ".join(hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url=f"https://www.br.dk/kundeservice/find-butik/{sn}/c/{sn}/",
            location_name=poi["name"],
            street_address=poi["address"]["street"],
            city=poi["address"]["city"],
            state="",
            zip_postal=poi["address"]["zip"],
            country_code=poi["address"]["country"],
            store_number=poi["sapSiteId"],
            phone=poi["phoneNumber"],
            location_type="",
            latitude=poi["coordinates"][0],
            longitude=poi["coordinates"][1],
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
