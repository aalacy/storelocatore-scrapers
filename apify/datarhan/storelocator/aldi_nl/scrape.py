from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://uberall.com/api/storefinders/ALDINORDNL_8oqeY3lnn9MTZdVzFn4o0WCDVTauoZ/locations/all?v=20211005&language=nl&fieldMask=id&fieldMask=identifier&fieldMask=googlePlaceId&fieldMask=lat&fieldMask=lng&fieldMask=name&fieldMask=country&fieldMask=city&fieldMask=province&fieldMask=streetAndNumber&fieldMask=zip&fieldMask=businessId&fieldMask=addressExtra&"
    domain = "aldi.nl"

    data = session.get(start_url).json()
    for poi in data["response"]["locations"]:
        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.aldi.nl/supermarkt.html",
            location_name=poi["name"],
            street_address=poi["streetAndNumber"],
            city=poi["city"],
            state=poi["province"],
            zip_postal=poi["zip"],
            country_code=poi["country"],
            store_number=poi["id"],
            phone="",
            location_type="",
            latitude=poi["lat"],
            longitude=poi["lng"],
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
