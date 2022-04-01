# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://api.quick.fr/v2/stores/store/locator?bbox=42.26934594596151%2C-8.163851305988823%2C51.0346270866046%2C12.490445569011177&services="
    domain = "quick.fr"

    all_locations = session.get(start_url).json()
    for poi in all_locations:
        page_url = "https://www.quick.fr/" + poi["slug"]
        hoo = []
        if poi["opening_hours"]:
            for day, hours in poi["opening_hours"].items():
                hoo.append(f"{day}: {hours[0]}-{hours[1]}")
        hoo = " ".join(hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["name"],
            street_address=poi["address"],
            city=poi["city"],
            state="",
            zip_postal=poi["postal_code"],
            country_code=poi["country"],
            store_number=poi["id"],
            phone=poi["phone"],
            location_type=poi["type"],
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
