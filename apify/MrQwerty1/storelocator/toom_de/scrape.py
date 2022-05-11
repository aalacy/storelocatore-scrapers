from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://api.toom.de/public/api/markets"
    r = session.get(api, headers=headers)
    js = r.json()["markets"]

    for j in js:
        slug = j.get("link")
        page_url = f"https://toom.de{slug}"
        location_name = j.get("name")

        a = j.get("address") or {}
        street_address = a.get("street")
        city = a.get("city")
        postal = a.get("zip")
        country_code = "DE"
        store_number = j.get("id")
        phone = j.get("phone")
        latitude = a.get("latitude")
        longitude = a.get("longitude")

        _tmp = []
        hours = j.get("openingTimes") or []
        for h in hours:
            day = h.get("label")
            try:
                start = h["value"]["opening"]
                end = h["value"]["closing"]
            except KeyError:
                _tmp.append(f"{day}: Closed")
                continue
            _tmp.append(f"{day}: {start}-{end}")

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
            hours_of_operation=hours_of_operation,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://toom.de/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
