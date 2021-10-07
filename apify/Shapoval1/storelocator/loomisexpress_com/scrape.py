from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from concurrent import futures


def get_data(coords, sgw: SgWriter):
    lat, long = coords
    locator_domain = "https://loomisexpress.com/"
    api_url = "https://loomisexpress.com/loomship/Common/queryLocations"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://loomisexpress.com",
        "Connection": "keep-alive",
        "Referer": "https://loomisexpress.com/loomship/Shipping/DropOffLocations",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }
    data = (
        '{"origin_lat":'
        + str(lat)
        + ',"origin_lng":'
        + str(long)
        + ',"include_otc":true,"include_smart":false,"include_terminal":false,"limit":500,"within_distance":100000}'
    )

    session = SgRequests()

    r = session.post(api_url, headers=headers, data=data)
    js = r.json()

    for j in js:

        page_url = "https://loomisexpress.com/loomship/Shipping/DropOffLocations"
        location_name = j.get("name") or "<MISSING>"
        street_address = f"{j.get('address_line_1')} {j.get('address_line_2')}"
        city = j.get("city") or "<MISSING>"
        state = j.get("province") or "<MISSING>"
        postal = j.get("postal_code") or "<MISSING>"
        country_code = "CA"
        phone = j.get("phone") or "<MISSING>"
        if "MON-FRI: 08:30-1" in phone:
            phone = "<MISSING>"
        latitude = j.get("latLng")[0]
        longitude = j.get("latLng")[1]
        hours_of_operation = (
            "".join(j.get("attention")).replace(". Loca", "").replace("<b", "").strip()
            or "<MISSING>"
        )

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
        country_codes=[SearchableCountries.CANADA],
        max_search_distance_miles=70,
        expected_search_radius_miles=70,
        max_search_results=None,
    )

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in coords}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.GeoSpatialId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        fetch_data(writer)
