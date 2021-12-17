from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api_url = "https://locations.nekterjuicebar.com/modules/multilocation/?near_location=75022&threshold=5000&published=1&within_business=true&limit=1000"

    r = session.get(api_url, headers=headers)
    js = r.json()["objects"]

    for j in js:
        street_address = f"{j.get('street')} {j.get('street2') or ''}".strip()
        city = j.get("city")
        state = j.get("state")
        postal = j.get("postal_code")
        country_code = j.get("country")
        store_number = j.get("partner_location_id")
        page_url = j.get("homepage_url") or "<MISSING>"
        location_name = j.get("location_name")
        phone = j.get("phones")[0].get("number")
        latitude = j.get("lat")
        longitude = j.get("lon")

        _tmp = []
        hours = j.get("formatted_hours", {}).get("primary", {}).get("days") or []
        for h in hours:
            day = h.get("label")
            time = h.get("content")
            _tmp.append(f"{day}: {time}")

        hours_of_operation = ";".join(_tmp)

        if hours_of_operation.count("Closed") == 7:
            hours_of_operation = "Closed"

        if phone[0] != "(" and phone != "<MISSING>":
            phone = SgRecord.MISSING
            hours_of_operation = "Coming Soon"

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
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://nekterjuicebar.com"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
