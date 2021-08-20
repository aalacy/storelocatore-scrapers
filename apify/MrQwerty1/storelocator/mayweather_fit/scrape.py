from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    api = "https://mayweather.fit/wp-admin/admin-ajax.php?action=cr_load_map_locations"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(api, headers=headers)
    js = r.json()

    for j in js:
        a = j.get("Address") or {}
        l = j.get("Location") or {}
        location_name = j.get("Name")
        page_url = "<INACCESSIBLE>"

        store_number = j.get("Id")
        street_address = a.get("Street")
        city = a.get("City")
        state = a.get("StateProv")
        postal = a.get("PostalCode")
        country_code = "US"
        phone = j.get("Phone")
        latitude = l.get("lat")
        longitude = l.get("lng")

        if "Your" in phone:
            continue

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=SgRecord.MISSING,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://mayweather.fit/"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
