from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch


def fetch_data(coords, sgw):
    lat, lng = coords
    api_url = f"https://www.johnstonmurphy.com/on/demandware.store/Sites-johnston-murphy-us-Site/en_US/Stores-GetStoresByLatLong?distance=null&lat={lat}&long={lng}"

    r = session.get(api_url)
    js = r.json()["stores"]

    for j in js:
        location_name = j.get("name")
        street_address = f"{j.get('address1')} {j.get('address2') or ''}".replace(
            "null", ""
        ).strip()
        city = j.get("city")
        state = j.get("stateCode")
        postal = j.get("postalCode") or ""
        postal = postal.replace("null", "")
        country_code = j.get("countryCode")
        store_number = j.get("ID")
        page_url = f"https://www.johnstonmurphy.com/on/demandware.store/Sites-johnston-murphy-us-Site/en_US/Stores-Details?StoreID={store_number}"
        phone = j.get("phone")
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        location_type = j.get("type") or ""
        if location_type not in {"Retail", "Factory"}:
            continue
        hours_of_operation = j.get("hours") or ""
        hours_of_operation = hours_of_operation.replace("\n", ";")
        if "closed" in hours_of_operation.lower() and "<" in hours_of_operation:
            hours_of_operation = "Closed"

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            store_number=store_number,
            location_type=location_type,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.johnstonmurphy.com/"
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.PageUrlId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        countries = [
            SearchableCountries.PANAMA,
            SearchableCountries.USA,
            SearchableCountries.CANADA,
            SearchableCountries.MEXICO,
        ]
        search = DynamicGeoSearch(
            country_codes=countries, expected_search_radius_miles=50
        )
        for coord in search:
            fetch_data(coord, writer)
