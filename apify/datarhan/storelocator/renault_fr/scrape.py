# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.renault.fr/wired/commerce/v1/dealers/locator?lat=46.28592337235003&lon=2.9234867520031003&country=fr&language=fr&count=250"
    domain = "renault.fr"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    all_locations = session.get(start_url, headers=hdr).json()
    for poi in all_locations:
        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.renault.fr/trouver-un-etablissement.html",
            location_name=poi["name"],
            street_address=poi["streetAddress"],
            city=poi["locality"],
            state="",
            zip_postal=poi.get("postalCode"),
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
