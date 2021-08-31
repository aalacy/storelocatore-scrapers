from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    start_url = "https://www.mcdonalds.hr/api/locations/"
    domain = "mcdonalds.hr"
    data = session.get(start_url).json()

    for poi in data["locations"]:
        hoo = poi["data"]["working_hours"].split(".")[-1].split()
        hoo = [e.strip() for e in hoo if e.strip()]
        hoo = " ".join(hoo)
        if "RESTORAN JE ZATVOREN ZBOG PREUREĐENJA" in hoo:
            continue

        item = SgRecord(
            locator_domain=domain,
            page_url="https://mcdonalds.hr/lokacije/",
            location_name=poi["data"]["name"],
            street_address=poi["data"]["address"],
            city=poi["data"]["city"],
            state=SgRecord.MISSING,
            zip_postal=SgRecord.MISSING,
            country_code="HR",
            store_number=poi["id"],
            phone=poi["data"]["phone"],
            location_type=SgRecord.MISSING,
            latitude=poi["lat"],
            longitude=poi["lng"],
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
