from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from concurrent import futures


def get_data(coords, sgw: SgWriter):
    lat, long = coords
    locator_domain = "https://www.pokeworks.com"
    api_url = f"https://api.thelevelup.com/v15/apps/1116/locations?fulfillment_types=pickup&lat={str(lat)}&lng={str(long)}&page_size=30"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
    }

    session = SgRequests()

    r = session.get(api_url, headers=headers)

    js = r.json()
    for j in js:
        page_url = "https://www.pokeworks.com/all-locations"
        a = j.get("location")
        location_name = a.get("name")
        street_address = a.get("street_address")
        state = a.get("region")
        postal = a.get("postal_code")
        country_code = "US"
        city = a.get("locality")
        latitude = a.get("latitude")
        longitude = a.get("longitude")
        phone = a.get("phone")
        hours_of_operation = "".join(a.get("hours")).replace("\r\n", " ").strip()

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


def fetch_data(sgw: SgWriter):
    coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        max_search_distance_miles=600,
        expected_search_radius_miles=50,
        max_search_results=None,
    )

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in coords}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
