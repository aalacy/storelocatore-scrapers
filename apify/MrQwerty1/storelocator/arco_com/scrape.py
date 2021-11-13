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
        location_name = j.get("StoreName") or ""
        location_name = location_name.replace("&#44;", ",")
        street_address = j.get("Address") or ""
        city = j.get("City") or ""
        state = j.get("State") or ""
        postal = j.get("Zip")
        country_code = "US"
        store_number = j.get("StoreNumber")
        phone = j.get("Phone") or ""
        latitude = j.get("Lat") or ""
        longitude = j.get("Lng") or ""

        if "." not in latitude:
            continue
        if len(state.strip()) > 2 or state.lower() == "bc" or state == "":
            country_code = "MX"

        row = SgRecord(
            location_name=location_name.strip(),
            street_address=street_address.replace("&#44;", ",").strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone.strip(),
            latitude=latitude.strip(),
            longitude=longitude.strip(),
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.arco.com"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
