import json
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://chatzconnect.co.za/wp-admin/admin-ajax.php?action=asl_load_stores&nonce=cdfde00d59&load_all=1&layout=1"
    r = session.get(api, headers=headers)

    for j in r.json():
        location_name = j.get("title")
        latitude = j.get("lat") or ""
        longitude = j.get("lng") or ""
        phone = j.get("phone")
        store_number = j.get("id")
        street_address = f'{j.get("street")} {j.get("street2") or ""}'.strip()
        city = j.get("city")
        state = j.get("state")
        postal = j.get("postal_code")

        _tmp = []
        source = j.get("open_hours") or "{}"
        hours = json.loads(source)
        for k, v in hours.items():
            if v == "0":
                continue
            _tmp.append(f'{k}: {"".join(v)}')
        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="ZA",
            phone=phone,
            store_number=store_number,
            latitude=latitude.replace(",", "."),
            longitude=longitude.replace(",", "."),
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://chatzconnect.co.za/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
    }

    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
