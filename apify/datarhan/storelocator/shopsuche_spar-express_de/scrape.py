from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = (
        "https://api.shopsuche.spar-express.de/sparexpressstores?page=0&size=500"
    )
    domain = "spar-express.de"
    data = session.get(start_url).json()
    for poi in data["entries"]:

        item = SgRecord(
            locator_domain=domain,
            page_url="https://shopsuche.spar-express.de/",
            location_name=poi["name"],
            street_address=poi["street"],
            city=poi["city"],
            state="",
            zip_postal=poi["zipCode"],
            country_code="",
            store_number="",
            phone=poi["phone"],
            location_type=poi["type"],
            latitude=poi["geo"]["lat"],
            longitude=poi["geo"]["lon"],
            hours_of_operation=poi["openingHours"].replace(";", " "),
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
