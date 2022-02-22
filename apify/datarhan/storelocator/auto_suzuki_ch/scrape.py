import re
from yaml import load, CLoader as Loader

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://auto.suzuki.ch/haendler/"
    domain = "auto.suzuki.ch"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    all_locations = re.findall(
        r"locations\[\d+\] = (.+?)google.maps.event", response.text.replace("\n", "")
    )
    for poi in all_locations:
        poi = load(poi, Loader=Loader)

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=poi["locationData"]["organisation"],
            street_address=poi["locationData"]["address"],
            city=poi["locationData"]["city"],
            state="",
            zip_postal=poi["locationData"]["zip"],
            country_code="CH",
            store_number=poi["locationData"]["uid"],
            phone=poi["locationData"]["telephone"],
            location_type="",
            latitude=poi["marker"]["lat"],
            longitude=poi["marker"]["lon"],
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
