# -*- coding: utf-8 -*-
# --extra-index-url https://dl.cloudsmith.io/KVaWma76J5VNwrOm/crawl/crawl/python/simple/
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.wong.pe/files/PE-districts.json"
    domain = "wong.pe"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    all_locations = session.get(start_url, headers=hdr).json()
    for poi in all_locations:
        geo = poi["geoCoordinates"]
        zip_code = poi["zipList"][0] if poi.get("zipList") else ""
        hoo = poi["schedule"][0] if poi.get("schedule") else ""
        if "Metro" in poi["name"]:
            continue
        street_address = poi["address"]
        if poi["name"] == "Wong Panorama":
            street_address = "Av. Javier Prado Este Sublote 4B-4C"
            hoo = "Lunes a Domingo de 8:00 a.m. a 10:00 p.m."

        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.wong.pe/institucional/nuestras-tiendas",
            location_name=poi["name"],
            street_address=street_address,
            city="",
            state="",
            zip_postal=zip_code,
            country_code="",
            store_number=poi["id"],
            phone=poi["phone"],
            location_type="",
            latitude=geo[0],
            longitude=geo[1],
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
