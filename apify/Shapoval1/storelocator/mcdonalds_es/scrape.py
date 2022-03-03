from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from concurrent import futures


def get_data(coords, sgw: SgWriter):
    lat, long = coords
    locator_domain = "https://mcdonalds.es/"
    api_url = f"https://mcdonalds.es/api/restaurants?lat={str(lat)}&lng={str(long)}&radius=5000"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    }

    session = SgRequests()

    r = session.get(api_url, headers=headers)

    js = r.json()["restaurants"]

    for j in js:

        page_url = "https://mcdonalds.es/restaurantes"
        location_name = j.get("name") or "<MISSING>"
        street_address = j.get("address") or "<MISSING>"
        city = j.get("city") or "<MISSING>"
        state = j.get("province") or "<MISSING>"
        postal = j.get("cp") or "<MISSING>"
        country_code = "ES"
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        try:
            hours_of_operation = f"Week {j.get('schedules').get('restaurant').get('week').get('start')} - {j.get('schedules').get('restaurant').get('week').get('end')} Weekend {j.get('schedules').get('restaurant').get('weekend').get('start')} - {j.get('schedules').get('restaurant').get('weekend').get('end')}"
        except:
            hours_of_operation = "<MISSING>"
        if hours_of_operation == "Week  -  Weekend  - ":
            hours_of_operation = "<MISSING>"

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
        country_codes=[SearchableCountries.SPAIN],
        max_search_distance_miles=500000,
        expected_search_radius_miles=1,
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
