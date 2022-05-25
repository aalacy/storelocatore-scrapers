from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://easylocator.net/ajax/search_by_lat_lon_geojson/Magoos%20Locations%20Map/40.752/-73.995/0/100/null/null"
    r = session.get(api, headers=headers)
    js = r.json()["physical"]

    for j in js:
        j = j.get("properties") or {}
        location_name = j.get("name") or ""
        if "|" in location_name:
            location_name = location_name.split("|")[0].strip()
        adr1 = j.get("street_address") or ""
        adr2 = j.get("street_address_line2") or ""
        street_address = f"{adr1} {adr2}".strip()
        city = j.get("city")
        state = j.get("state_province")
        postal = j.get("zip_postal_code")
        country_code = "US"
        store_number = j.get("location_number")
        phone = j.get("phone")
        latitude = j.get("lat")
        longitude = j.get("lon")

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
    locator_domain = "https://magoospet.com/"
    page_url = "https://magoospet.com/20069/Store-Locator/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
