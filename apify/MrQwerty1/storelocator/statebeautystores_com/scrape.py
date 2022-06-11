from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://statebeautystores.com/admin/module.ajax.public.php?m=sbs_store_locator_by_state&distance=&instance_name=_m_map_points&zipcode=&state=all&page_id=94&mf=public_data_locations_js"
    r = session.get(api, headers=headers)
    js = r.json()["features"]

    for j in js:
        g = j.get("geometry") or {}
        j = j.get("properties") or {}
        street_address = j.get("address") or ""
        if "(" in street_address:
            street_address = street_address.split("(")[0].strip()
        if "All" in street_address:
            street_address = street_address.split("All")[0].strip()
        city = j.get("city")
        state = j.get("state")
        postal = j.get("postalCode")
        country_code = "US"
        store_number = j.get("Id")
        location_name = city
        page_url = f"https://statebeautystores.com/state_map?id=state_map&state={state}"
        phone = j.get("phone")
        longitude, latitude = g.get("coordinates") or [
            SgRecord.MISSING,
            SgRecord.MISSING,
        ]

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
            store_number=store_number,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://statebeautystores.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
