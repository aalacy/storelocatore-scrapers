import csv
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    api = "https://www.arco.com/img/findstation/MasterArcoStoreLocations.csv"

    r = session.get(api)
    dr = csv.DictReader(r.content.decode("utf8").splitlines())

    for j in dr:
        location_name = j.get("StoreName")
        street_address = j.get("Address")
        city = j.get("City")
        state = j.get("State") or ""
        postal = j.get("Zip")
        country_code = "US"
        store_number = j.get("StoreNumber")
        phone = j.get("Phone") or ""
        latitude = j.get("Lat") or ""
        longitude = j.get("Lng")

        if len(state) > 2 or phone.startswith("52 ") or latitude.find(".") == -1:
            continue

        row = SgRecord(
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.arco.com"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
