# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = (
        "https://www.cardsdirect.co.uk/storefinder/index/loadstore/?websiteIds[]=1"
    )
    domain = "cardsdirect.co.uk"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    data = session.get(start_url, headers=hdr).json()

    for poi in data["stores"]:
        street_address = poi["address_line_1"]
        if poi["address_line_2"]:
            street_address += ", " + poi["address_line_2"]
        hoo = []
        for e in poi["opening_times"]["regular"]:
            hoo.append(f'{e["name"]}: {e["time_open"]} - {e["time_close"]}')
        hoo = " ".join(hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url=poi["website_url"],
            location_name=poi["name"],
            street_address=street_address,
            city=poi["city"],
            state=poi["county"],
            zip_postal=poi["postcode"],
            country_code=poi["country_id"],
            store_number=poi["store_id"],
            phone=poi["phone"],
            location_type="",
            latitude=poi["latitude"],
            longitude=poi["longitude"],
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
