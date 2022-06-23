# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.dacia.de/haendlersuche/liste-concessions.data"
    domain = "dacia.de"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    data = session.get(start_url, headers=hdr).json()
    all_locations = data["content"]["editorialZone"]["slice54vb"]["dealers"]["data"]
    total_pages = data["content"]["editorialZone"]["slice54vb"]["dealers"]["totalPages"]
    for p in range(2, int(total_pages) + 1):
        url = f"https://www.dacia.de/haendlersuche/liste-concessions.data?page={str(p)}"
        data = session.get(url, headers=hdr).json()
        all_locations += data["content"]["editorialZone"]["slice54vb"]["dealers"][
            "data"
        ]

    for poi in all_locations:
        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.dacia.de/haendlersuche/liste-concessions.html",
            location_name=poi["name"],
            street_address=poi["extendedAddress"],
            city=poi["locality"].split("/")[0],
            state="",
            zip_postal=poi["postalCode"],
            country_code=poi["country"],
            store_number=poi["dealerId"],
            phone=poi["telephone"].get("value"),
            location_type=poi["type"],
            latitude=poi.get("geolocalization", {}).get("lat"),
            longitude=poi.get("geolocalization", {}).get("lon"),
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
