# -*- coding: utf-8 -*-

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "https://www.cora.ro/contact-us"
    domain = "cora.ro"

    frm = {
        "form_key": "ITW3NmxCtezwd3PF",
        "isAjax": "1",
    }
    data = session.post(
        "https://www.cora.ro/storelocator/contact/index/", data=frm
    ).json()
    for store_number, poi in data.items():
        raw_address = poi["short_address"]
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=poi["name"],
            street_address=street_address,
            city=addr.city,
            state="",
            zip_postal=addr.postcode,
            country_code="RO",
            store_number=poi["store_id"],
            phone=poi["phone"],
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
            SgRecordID({SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STORE_NUMBER})
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
