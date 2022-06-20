# -*- coding: utf-8 -*-
# --extra-index-url https://dl.cloudsmith.io/KVaWma76J5VNwrOm/crawl/crawl/python/simple/
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://map.karttapalvelut.fi/ajax/getplaces/map_name/renault/lang/fi"
    domain = "renault.fi"

    all_locations = session.get(start_url).json()
    for poi in all_locations:
        for k, v in poi["fieldData"].items():
            if type(v) == str:
                if v and v.split()[0].isdigit():
                    if len(v.split()) > 2:
                        phone = v
        location_type = "Showroom"
        if not poi["fieldData"]["5669d73842145c112c3eb2ce"]:
            continue

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=poi["fieldData"]["Name"],
            street_address=poi["fieldData"]["Address"],
            city=poi["fieldData"]["City"],
            state="",
            zip_postal=poi["fieldData"]["Postcode"],
            country_code=poi["fieldData"]["Country"],
            store_number="",
            phone=phone,
            location_type=location_type,
            latitude=poi["coords"][0],
            longitude=poi["coords"][1],
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
