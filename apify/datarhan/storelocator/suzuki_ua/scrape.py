# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://api.storyblok.com/v1/cdn/stories/?starts_with=dealers/&per_page=100&version=draft&cv=1641902224942&token=sKFHamWi5medo2Zwu7rsIwtt"
    domain = "suzuki.ua"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    data = session.get(start_url, headers=hdr).json()
    for poi in data["stories"]:
        if not poi["content"]["isCars"] or not poi["content"]["isDealer"]:
            continue
        phone = [
            e["phone"] for e in poi["content"]["carsPhones"] if e["info"] == "Салон:"
        ]
        phone = phone[0] if phone else ""

        item = SgRecord(
            locator_domain=domain,
            page_url="https://suzuki.ua/buyers/dealers-center/",
            location_name=poi["name"],
            street_address=poi["content"]["address"],
            city=poi["content"]["city"],
            state=poi["content"]["regionName"],
            zip_postal="",
            country_code="UA",
            store_number=poi["content"]["id"],
            phone=phone,
            location_type="",
            latitude=poi["content"]["latitude"],
            longitude=poi["content"]["longitude"],
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
