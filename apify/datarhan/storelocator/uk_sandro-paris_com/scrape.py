# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "sandro-paris.com"
    start_url = "https://uk.sandro-paris.com/on/demandware.store/Sites-Sandro-UK-Site/en_GB/Stores-GetStores"
    all_locations = session.get(start_url).json()
    for poi in all_locations:
        location_name = poi["properties"]["title"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["properties"]["address"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["properties"]["city"]
        city = city if city else "<MISSING>"
        state = poi["properties"]["state"]
        state = state if state else "<MISSING>"
        zip_code = poi["properties"]["zip"]
        zip_code = zip_code.strip() if zip_code else "<MISSING>"
        if len(zip_code) > 5:
            state = zip_code[:2]
            zip_code = zip_code[2:].strip()
        country_code = poi["properties"]["countryCode"]
        store_number = poi["id"]
        phone = poi["properties"]["phone"]
        phone = phone if phone and phone != "0" else "<MISSING>"
        latitude = poi["lat"]
        longitude = poi["lng"]
        hoo = []
        if poi["properties"].get("storeHours"):
            days = [
                "Sunday",
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
            ]
            hours = poi["properties"]["storeHours"].split(" | ")
            hoo = list(map(lambda d, h: d + " " + h, days, hours))
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

        item = SgRecord(
            locator_domain=domain,
            page_url="https://uk.sandro-paris.com/en/stores",
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type="",
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
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
