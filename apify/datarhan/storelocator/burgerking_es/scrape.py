from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    start_url = "https://static.burgerkingencasa.es/bkhomewebsite/es/stores_es.json"
    domain = "burgerking.es"
    data = session.get(start_url).json()

    all_locations = data["stores"]
    for poi in all_locations:
        if not poi["address"]:
            continue
        days = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]
        hoo = []
        for day in days:
            hoo.append(f"{day} {poi[day]}")
        hours_of_operation = " ".join(hoo)
        latitude = poi["latitude"]
        if latitude == "0.000000":
            latitude = SgRecord.MISSING
        longitude = poi["longitude"]
        if longitude == "0.000000":
            longitude = SgRecord.MISSING
        zip_code = poi["postalcode"]
        if zip_code.isnumeric() and len(zip_code) < 5:
            zip_code = "0" + zip_code
        if zip_code.endswith("."):
            zip_code = zip_code[:-1]

        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.burgerking.es/hiring",
            location_name=poi["address"],
            street_address=poi["address"],
            city=poi["city"],
            state=SgRecord.MISSING,
            zip_postal=zip_code,
            country_code="ES",
            store_number=poi["bkcode"],
            phone=SgRecord.MISSING,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.STORE_NUMBER, SgRecord.Headers.STREET_ADDRESS})
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
