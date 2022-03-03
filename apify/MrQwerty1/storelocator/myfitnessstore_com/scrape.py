import json
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://myfitnessstore.com/wp-admin/admin-ajax.php?action=asl_load_stores&load_all=1&layout=1"
    page_url = "https://myfitnessstore.com/retail-locator/"
    r = session.get(api, headers=headers)
    js = r.json()

    for j in js:
        location_name = j.get("title") or ""
        location_name = location_name.split(" now ")[0]
        street_address = j.get("street")
        city = j.get("city")
        state = j.get("state")
        postal = j.get("postal_code")
        country = j.get("country")

        phone = j.get("phone")
        latitude = j.get("lat")
        longitude = j.get("lng")
        store_number = j.get("id")

        _tmp = []
        text = j.get("open_hours") or ""
        if text:
            hours = json.loads(text)
        else:
            hours = {}

        for day, inter in hours.items():
            if inter != "0":
                _tmp.append(f"{day}: {inter}")
        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country,
            store_number=store_number,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://myfitnessstore.com/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
        "Accept": "*/*",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
