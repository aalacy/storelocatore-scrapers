# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()
    domain = "sandro-paris.com"
    start_url = "https://uk.sandro-paris.com/on/demandware.store/Sites-Sandro-UK-Site/en_GB/Stores-GetStores"
    all_locations = session.get(start_url).json()
    for poi in all_locations:
        location_name = poi["properties"]["title"]
        raw_address = f'{poi["properties"]["address"]}, {poi["properties"]["city"]}, {poi["properties"]["state"]}, {poi["properties"]["zip"]}'
        addr = parse_address_intl(raw_address.replace("None", ""))
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += ", " + addr.street_address_2
        street_address = street_address.replace("None", "")
        if street_address.endswith("."):
            street_address = street_address[:-1]
        city = addr.city
        if city:
            city = city.replace("None", "")
        if city and len(city) == 3:
            city = ""
        if city and city.endswith("."):
            city = city[:-1]
        state = addr.state
        if state:
            state = state.replace("None", "")
        if state and "." in state:
            state = ""
        zip_code = addr.postcode
        if zip_code:
            zip_code = zip_code.replace("None", "").replace("NONE", "")
        country_code = poi["properties"]["countryCode"]
        store_number = poi["id"]
        phone = poi["properties"]["phone"]
        phone = phone if phone and phone != "0" else ""
        if "A COMPLETER LIVRAISO" in phone:
            phone = ""
        if phone:
            phone = phone.split("/")[0].strip()
        if phone == "-":
            phone = ""
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
        hours_of_operation = " ".join(hoo) if hoo else ""

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
            raw_address=raw_address.replace(" None,", ""),
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
