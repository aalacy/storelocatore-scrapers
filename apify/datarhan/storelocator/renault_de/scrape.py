# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.renault.de/wired/commerce/v1/dealers/locator?lat=51.05917485433858&lon=9.417555934754745&country=de&language=de&filters=renault.blacklisted%3D%3Dfalse&count=250"
    page_urls = {"www.renault.de": "https://www.renault.de/haendlersuche.html"}
    domain = "renault.de"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    all_locations = session.get(start_url, headers=hdr).json()
    for poi in all_locations:
        item = SgRecord(
            locator_domain=domain,
            page_url=page_urls[start_url.split("/")[2]],
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
