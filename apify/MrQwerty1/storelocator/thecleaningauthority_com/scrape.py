from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://www.thecleaningauthority.com/locations/?CallAjax=GetLocations"
    r = session.get(api, cookies=cookies)
    js = r.json()

    for j in js:
        location_name = j.get("BusinessName")
        slug = j.get("Path")
        page_url = f"https://www.thecleaningauthority.com{slug}"
        street_address = f'{j.get("Address1")} {j.get("Address2") or ""}'.strip()
        city = j.get("City")
        state = j.get("State")
        postal = j.get("ZipCode")

        phone = j.get("Phone")
        latitude = j.get("Latitude")
        longitude = j.get("Longitude")
        store_number = j.get("FranchiseLocationID")

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="US",
            store_number=store_number,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.thecleaningauthority.com/"
    cookies = {"_z": "75022"}
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
