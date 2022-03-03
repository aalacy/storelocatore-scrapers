from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://www.aldoshoes.co.il/available/store/stores"
    page_url = "https://www.aldoshoes.co.il/#stores"
    r = session.get(api)
    js = r.json()

    for j in js.values():
        location_name = j.get("name")
        street_address = j.get("address")
        phone = j.get("phone")
        if str(phone) == "0":
            phone = SgRecord.MISSING
        city = j.get("city")
        state = j.get("area")
        latitude = j.get("store_latitude")
        longitude = j.get("store_longitude")
        store_number = j.get("branch_id")

        _tmp = []
        hours = j.get("opening_times") or {}
        for k, v in hours.items():
            if not v.get("is_open"):
                _tmp.append(f"{k}: Closed")
                continue

            start = v.get("open")
            end = v.get("close")
            _tmp.append(f"{k}: {start}-{end}")

        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            country_code="IL",
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            store_number=store_number,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.aldoshoes.co.il/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
