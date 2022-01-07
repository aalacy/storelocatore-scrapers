from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter

base_url = "https://arthurmurray.com/assets/data/locations.json"
domain = "arthurmurray.com"


def fetch_data():
    with SgRequests() as session:
        for poi in session.get(base_url).json():
            page_url = "https://arthurmurray.com/locations/" + poi["slug"]
            street_address = poi["address"]
            if poi["address2"]:
                street_address += ", " + poi["address2"]

            yield SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=poi["name"],
                street_address=street_address,
                city=poi["city"],
                state=poi["state"],
                zip_postal=poi["postal"],
                country_code=poi["country"],
                store_number="",
                phone=poi["phone"],
                location_type="",
                latitude=poi["lat"],
                longitude=poi["lng"],
                hours_of_operation=poi["hours1"],
            )


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
