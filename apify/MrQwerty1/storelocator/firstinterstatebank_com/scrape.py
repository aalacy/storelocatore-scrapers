from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://www.firstinterstatebank.com/core/cache/locations.cache"
    r = session.get(api, headers=headers)
    js = r.json()

    for j in js:
        street_address = j.get("address")
        city = j.get("city")
        state = j.get("state")
        postal = j.get("zip")
        country_code = "US"
        store_number = j.get("id")
        location_name = j.get("name")
        location_type = j.get("type") or ""
        if location_type.count("ATM") > 1:
            if "Branch" in location_type:
                location_type = "Branch, ATM"
            else:
                location_type = "ATM"
        phone = j.get("phone")
        latitude = j.get("latitude")
        longitude = j.get("longitude")

        hours_of_operation = j.get("lobby_hours")
        if not hours_of_operation:
            hours_of_operation = j.get("driveup_hours")

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
            location_type=location_type,
            hours_of_operation=hours_of_operation,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.firstinterstatebank.com/"
    page_url = "https://www.firstinterstatebank.com/locations/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
