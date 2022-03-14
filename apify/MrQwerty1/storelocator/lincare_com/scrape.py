from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://www.lincare.com/api/LocationSearch/LocationSearch?skip=0&take=1000"
    r = session.get(api, headers=headers)
    js = r.json()["documents"]

    for j in js:
        adr1 = j.get("Address1") or ""
        adr2 = j.get("Address2") or ""
        street_address = f"{adr1} {adr2}".strip()
        city = j.get("City")
        state = j.get("State")
        postal = j.get("ZipCode")
        country_code = "US"
        store_number = j.get("Id")
        name = j.get("Name") or ""
        part = j.get("MarketingName") or ""
        location_name = f"{name} - {part}"
        slug = j.get("LocationDetailPageLink")
        page_url = f"https://www.lincare.com{slug}"
        phone = j.get("Phone")
        latitude = j.get("Lat")
        longitude = j.get("Lon")

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
    locator_domain = "https://www.lincare.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
