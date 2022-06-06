from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://api.karwei.nl/store/1/"
    r = session.get(api, headers=headers)
    js = r.json()

    for j in js:
        location_name = j.get("name")
        slug = j.get("slug") or ""
        page_url = f"https://www.karwei.nl/vestigingen/{slug}"

        a = j.get("address") or {}
        street_address = f'{a.get("street")} {a.get("streetNumber") or ""}'.strip()
        city = a.get("city")
        state = a.get("state")
        postal = a.get("postalCode")
        phone = a.get("phone")

        g = j.get("geoPoint") or {}
        latitude = g.get("latitude")
        longitude = g.get("longitude")
        store_number = j.get("uid")

        _tmp = []
        hours = j.get("regularOpeningHours") or []
        for h in hours:
            day = h.get("dayOfWeek")
            start = h.get("opens")
            end = h.get("closes")
            if not start:
                _tmp.append(f"{day}: Closed")
            else:
                _tmp.append(f"{day}: {start}-{end}")

        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="NL",
            store_number=store_number,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.karwei.nl/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
        "Accept": "*/*",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
