import json
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://www.mrpretzelsuk.com/wp-admin/admin-ajax.php?action=asl_load_stores&load_all=1&layout=1"
    r = session.get(api, headers=headers)
    js = r.json()

    for j in js:
        street_address = j.get("street")
        city = j.get("city")
        postal = j.get("postal_code")
        country_code = "GB"
        store_number = j.get("id")
        location_name = j.get("title")
        phone = j.get("phone")
        latitude = j.get("lat") or ""
        longitude = j.get("lng") or ""
        if latitude == "0.0":
            latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

        _tmp = []
        text = j.get("open_hours") or "{}"
        hours = json.loads(text)
        for day, v in hours.items():
            inter = "".join(v)
            if inter == "0":
                continue
            _tmp.append(f"{day}: {inter}")

        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            store_number=store_number,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.mrpretzelsuk.com/"
    page_url = "https://www.mrpretzelsuk.com/outlets/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
