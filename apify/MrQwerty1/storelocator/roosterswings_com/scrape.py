from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch


def fetch_data(coords, sgw):
    lat, lon = coords
    data = {"lat": lat, "lng": lon}

    r = session.post(
        "https://roosterswings.com/assets/inc/map_query.php", data=data, headers=headers
    )
    js = r.json()["locations"]

    for j in js:
        page_url = (
            f'https://roosterswings.com/locations/view-all-locations/{j.get("slug")}'
        )
        location_name = j.get("location_name").strip()
        street_address = j.get("address")
        city = j.get("city")
        state = j.get("state")
        postal = j.get("zip")
        country_code = "US"
        store_number = j.get("id")
        phone = j.get("phone")
        latitude = j.get("lat")
        longitude = j.get("long")
        location_type = j.get("type")

        _tmp = []
        for i in range(1, 5):
            line = j.get(f"hours_{i}")
            if line:
                _tmp.append(line)

        hours_of_operation = ";".join(_tmp)

        if j.get("coming_soon") == "1":
            hours_of_operation = "Coming Soon"

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
    locator_domain = "https://roosterswings.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0",
        "Accept": "*/*",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://roosterswings.com",
        "Connection": "keep-alive",
        "Referer": "https://roosterswings.com/locations/view-all-locations/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.PageUrlId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        countries = [SearchableCountries.USA]
        search = DynamicGeoSearch(
            country_codes=countries, expected_search_radius_miles=50
        )
        for coord in search:
            fetch_data(coord, writer)
