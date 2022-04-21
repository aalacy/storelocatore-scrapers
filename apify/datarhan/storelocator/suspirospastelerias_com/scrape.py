# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "https://www.suspirospastelerias.com/api/api/cms/stores"
    domain = "suspirospastelerias.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    all_locations = session.get(start_url, headers=hdr).json()
    for poi in all_locations:
        raw_address = poi["address"]
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        zip_code = addr.postcode
        if zip_code:
            zip_code = (
                zip_code.replace("C.P.", "")
                .replace("AZ.", "")
                .replace("C.P", "")
                .replace("CP", "")
                .replace("CP.", "")
                .replace("C. P.", "")
                .replace(".", "")
            )
            if "SECC" in zip_code:
                zip_code = ""
            if len(zip_code) < 4:
                zip_code = ""
        phone = poi["phoneNumber"]
        if len(phone) == 1:
            phone = ""
        state = addr.state
        if state:
            state = state.replace(".", "")

        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.suspirospastelerias.com/mx/es/tienda/sucursales",
            location_name=poi["name"],
            street_address=street_address,
            city=poi["city"]["name"],
            state=state,
            zip_postal=zip_code,
            country_code=poi["city"]["country"],
            store_number="",
            phone=phone,
            location_type="",
            latitude=poi["latitude"],
            longitude=poi["longitude"],
            hours_of_operation=poi["hours"],
            raw_address=raw_address,
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
