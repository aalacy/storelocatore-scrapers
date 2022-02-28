from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://www.waitrose.ae/api/v1/stores/?format=json&page_size=1000"
    r = session.get(api, headers=headers)
    js = r.json()["results"]

    for j in js:
        location_name = j.get("name")

        a = j.get("address") or {}
        street_address = f'{a.get("line1")} {a.get("line2") or ""}'.strip()
        city = a.get("state") or SgRecord.MISSING
        state = a.get("state")
        postal = a.get("postcode")
        country = a.get("country")
        if "dubai" in street_address.lower() and city == SgRecord.MISSING:
            city = "Dubai"
            state = "Dubai"

        phone = j.get("phone")
        latitude = a.get("latitude")
        longitude = a.get("longitude")

        _tmp = []
        hours = j.get("opening_periods") or []
        for h in hours:
            day = h.get("get_weekday_display")
            start = h.get("start")
            end = h.get("end")
            _tmp.append(f"{day}: {start}-{end}")

        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.waitrose.ae/"
    page_url = "https://www.waitrose.ae/en/store-locator/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
        "Accept": "*/*",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
