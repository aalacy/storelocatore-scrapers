# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.dacia.fi/jalleenmyyjat/"
    domain = "dacia.fi"
    all_locations = session.get(
        "https://map.karttapalvelut.fi/ajax/getplaces/map_name/dacia/lang/fi"
    ).json()
    phone = ""
    for poi in all_locations:
        for k, v in poi["fieldData"].items():
            if type(v) == str:
                if v and v.split()[0].isdigit():
                    if len(v.split()) > 2:
                        phone = v
        location_type = "Myynti"
        if not poi["fieldData"]["56c9630f42145cae3f00bb74"]:
            location_type = "Huolto"

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
