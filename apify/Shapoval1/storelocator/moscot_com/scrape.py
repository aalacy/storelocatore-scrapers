from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from concurrent import futures


def get_data(coords, sgw: SgWriter):
    lat, long = coords
    locator_domain = "https://moscot.com/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
    }

    session = SgRequests()

    r = session.get(
        f"https://stockist.co/api/v1/u2740/locations/search?latitude={lat}&longitude={long}&distance=500000",
        headers=headers,
    )
    js = r.json()["locations"]

    for j in js:

        page_url = "https://moscot.com/pages/locations"
        location_name = j.get("name")
        street_address = (
            f"{j.get('address_line_1')} {j.get('address_line_2') or ''}".strip()
            or "<MISSING>"
        )
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("postal_code") or "<MISSING>"
        country_code = j.get("country") or "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
        if "".join(phone).find("/") != -1:
            phone = phone.split("/")[0].strip()
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        store_number = j.get("id") or "<MISSING>"

        row = SgRecord(
            locator_domain=locator_domain,
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
            hours_of_operation=SgRecord.MISSING,
        )

        sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    for country in SearchableCountries.ALL:
        coords = DynamicGeoSearch(
            country_codes=[f"{country}"],
            max_search_distance_miles=100,
            expected_search_radius_miles=100,
            max_search_results=None,
        )

        with futures.ThreadPoolExecutor(max_workers=7) as executor:
            future_to_url = {executor.submit(get_data, url, sgw): url for url in coords}
            for future in futures.as_completed(future_to_url):
                future.result()


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LOCATION_NAME}
            ),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        fetch_data(writer)
