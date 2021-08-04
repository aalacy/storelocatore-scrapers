from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    api_url = "https://api.freshop.com/1/stores?app_key=chief_markets&has_address=true&is_selectable=true&limit=100&token=3ebbca6a16db158e53f6ada14138d9b1"
    session = SgRequests()
    r = session.get(api_url)
    js = r.json()
    for j in js["items"]:
        street_address = j.get("address_1")
        phone = "".join(j.get("phone_md")).split("Fax")[0].replace("Phone:", "").strip()
        city = j.get("city")
        postal = j.get("postal_code")
        state = j.get("state")
        country_code = "US"
        page_url = j.get("url")
        location_name = j.get("name")
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        hours_of_operation = j.get("hours_md")

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
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.chiefmarkets.com"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
