from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://www.christushealth.org/api/doctorlocations/locations"
    r = session.get(api, headers=headers)
    js = r.json()["items"]

    for j in js:
        adr1 = j.get("streetAddress") or ""
        adr2 = j.get("streetAddress2") or ""
        street_address = f"{adr1} {adr2}".strip()
        city = j.get("city")
        state = j.get("state")
        postal = j.get("zipCode")
        country_code = "US"
        store_number = j.get("id")
        entity = j.get("entity")
        if entity != "CHRISTUS":
            continue
        location_type = j.get("type")
        location_name = j.get("name")
        slug = j.get("url")
        page_url = f"https://www.christushealth.org{slug}"
        phone = j.get("phone")
        latitude = j.get("latitude")
        longitude = j.get("longitude")

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
            location_type=location_type,
            phone=phone,
            store_number=store_number,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.christushealth.org/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
