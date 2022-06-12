from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://api.candidco.com/api/v1/studios/"
    r = session.get(api)
    js = r.json()

    for j in js:
        location_type = j.get("studio_type") or ""
        if location_type != "retail":
            continue

        a = j.get("studio_address")
        street_address = f"{a.get('thoroughfare')} {a.get('premise') or ''}".strip()
        city = a.get("locality")
        state = a.get("state_name")
        postal = a.get("postal_code")
        country_code = a.get("country")
        store_number = j.get("id")
        page_url = (
            f'https://candidco.com/studios/{j["studio_region"]["slug"]}/{j.get("slug")}'
        )
        location_name = j.get("name")
        phone = j.get("phone")
        latitude = a.get("latitude")
        longitude = a.get("longitude")

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            location_type=location_type,
            store_number=store_number,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://candidco.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
