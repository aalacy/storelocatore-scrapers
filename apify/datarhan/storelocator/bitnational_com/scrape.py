from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    start_url = "https://api.storerocket.io/api/user/5Z4wDxjJPd/locations?radius=250&units=kilometers"
    domain = "bitnational.com"
    data = session.get(start_url).json()

    all_locations = data["results"]["locations"]
    for poi in all_locations:
        hoo = []
        for day, hours in poi["hours"].items():
            hoo.append(f"{day} {hours}")
        hours_of_operation = " ".join(hoo)
        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.bitnational.com/bitcoinatm?location=" + poi["slug"],
            location_name=poi["name"],
            street_address=poi["address_line_1"],
            city=poi["city"],
            state=poi["state"],
            zip_postal=SgRecord.MISSING,
            country_code=poi["country"],
            store_number=poi["id"],
            phone=SgRecord.MISSING,
            location_type=SgRecord.MISSING,
            latitude=poi["lat"],
            longitude=poi["lng"],
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
