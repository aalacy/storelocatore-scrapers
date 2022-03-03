from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://api.vold.io/5b39cd517169294aba251f43/store?sort=id+DESC&limit=2000&where={%22status%22%3A%22published%22}&skip=0"
    r = session.get(api)

    for j in r.json()["results"]:
        location_name = j.get("title") or ""
        loc = j.get("location") or {}
        street_address = loc.get("address") or ""
        if street_address.endswith(","):
            street_address = street_address[:-1]
        city = loc.get("city")
        state = loc.get("province")
        postal = loc.get("zipcode")
        country = loc.get("country")
        phone = loc.get("phone")
        longitude, latitude = loc.get("coordinates") or (
            SgRecord.MISSING,
            SgRecord.MISSING,
        )
        location_type = SgRecord.MISSING
        if "soon" in location_name.lower():
            location_type = "Coming Soon"

        _tmp = []
        hours = j.get("schedule") or []
        for h in hours:
            day = h.get("day")
            start = h.get("open")
            end = h.get("close")
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
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.jcodonuts.com/"
    page_url = "https://www.jcodonuts.com/id/en/stores#"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
