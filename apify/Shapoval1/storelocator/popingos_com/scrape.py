from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://popingos.com"
    api_url = "https://api.storerocket.io/api/user/DMJbBjNJXe/locations?radius=50000&units=miles"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["results"]["locations"]

    for j in js:
        slug = j.get("slug")
        page_url = f"https://www.popingos.com/store-locator?location={slug}"
        location_name = j.get("name")
        location_type = j.get("location_type_name")
        street_address = f"{j.get('address_line_1')} {j.get('address_line_2')}".strip()
        phone = j.get("phone")
        state = j.get("state")
        postal = j.get("postcode")
        country_code = j.get("country")
        city = j.get("city")
        latitude = j.get("lat")
        longitude = j.get("lng")
        adr = j.get("address")
        hours_of_operation = f"Mon {j.get('mon')}; Tue {j.get('tue')}; Wed {j.get('wed')}; Thu {j.get('thu')}; Fri {j.get('fri')}; Sat {j.get('sat')}; Sun {j.get('sun')}"

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=adr,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://popingos.com"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
