# -*- coding: utf-8 -*-
import json

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://stockist.co/api/v1/u9787/locations/all.js?callback=_stockistAllStoresCallback"
    domain = "workworld.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    data = response.text.split("Callback(")[-1][:-2]

    all_locations = json.loads(data)
    for poi in all_locations:
        if "Whistle Workwear" in poi["name"]:
            continue
        street_address = poi["address_line_1"]
        if poi["address_line_2"]:
            street_address += ", " + poi["address_line_2"]

        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.workworld.com/password",
            location_name=poi["name"],
            street_address=street_address,
            city=poi["city"],
            state=poi["state"],
            zip_postal=poi["postal_code"],
            country_code=poi["country"],
            store_number=poi["id"],
            phone=poi["phone"],
            location_type="",
            latitude=poi["latitude"],
            longitude=poi["longitude"],
            hours_of_operation=" ".join(
                poi["description"].replace("Store Hours", "").split()
            ),
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
