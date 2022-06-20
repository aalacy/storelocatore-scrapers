import json
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://preunic.cl/map"
    r = session.get(api, headers=headers)
    text = r.text.split("var locations = ")[1].split("];")[0].replace("\\", "") + "]"
    js = json.loads(text)

    for j in js:
        street_address = j.get("address")
        city = j.get("city")
        state = j.get("state")
        postal = j.get("ZipCode")
        country_code = "CL"
        store_number = j.get("code")
        location_name = j.get("name")
        phone = j.get("phone") or ""
        if "tiene" in phone:
            phone = SgRecord.MISSING
        latitude = j.get("lat")
        longitude = j.get("lng")
        location_type = j.get("store_type")
        hours_of_operation = j.get("schedules") or ""
        hours_of_operation = hours_of_operation.replace("u003cbru003e", ";")
        if hours_of_operation.endswith(";"):
            hours_of_operation = hours_of_operation[:-1]

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            location_type=location_type,
            store_number=store_number,
            hours_of_operation=hours_of_operation,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = page_url = "https://preunic.cl/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0",
        "Accept": "*/*;q=0.5, text/javascript, application/javascript, application/ecmascript, application/x-ecmascript",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
