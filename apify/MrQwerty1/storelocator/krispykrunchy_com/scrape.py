from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch


def fetch_data(sgw: SgWriter):
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=30
    )
    for lat, lng in search:
        api = f"https://krispykrunchy.com/wp-admin/admin-ajax.php?action=store_search&lat={lat}&lng={lng}&max_results=100&search_radius=50&autoload=1"
        r = session.get(api, headers=headers)
        js = r.json()

        for j in js:
            page_url = j.get("permalink")
            location_name = j.get("store") or ""
            location_name = (
                location_name.replace("&#8217;", "'")
                .replace("&#038;", "&")
                .replace("&#8211;", "-")
                .strip()
            )
            street_address = f"{j.get('address')} {j.get('address2') or ''}".strip()

            city = j.get("city")
            state = j.get("state")
            postal = j.get("zip") or ""
            if postal:
                if postal[0].isalpha():
                    postal = SgRecord.MISSING
            country_code = "US"
            store_number = j.get("id")
            phone = j.get("phone") or ""
            if "," in phone:
                phone = phone.split(",")[0].strip()
            if phone:
                if phone[0].isalpha() and phone[-1].isalpha():
                    phone = SgRecord.MISSING
            latitude = j.get("lat")
            longitude = j.get("lng")
            hours_of_operation = j.get("hours")

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
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://krispykrunchy.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        fetch_data(writer)
