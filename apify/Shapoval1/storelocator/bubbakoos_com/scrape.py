from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from concurrent import futures


def get_data(coords, sgw: SgWriter):
    lat, long = coords
    locator_domain = "https://www.bubbakoos.com/"
    api_url = f"https://api.thelevelup.com/v15/apps/1641/locations?fulfillment_types=pickup&lat={str(lat)}&lng={str(long)}&page_size=30"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    }

    session = SgRequests()

    r = session.get(api_url, headers=headers)

    js = r.json()

    for j in js:

        page_url = "https://www.bubbakoos.com/locations"
        a = j.get("location")
        location_name = f"{a.get('merchant_name')} {a.get('name')}"
        street_address = a.get("street_address") or "<MISSING>"
        city = a.get("locality") or "<MISSING>"
        state = a.get("region") or "<MISSING>"
        postal = a.get("postal_code") or "<MISSING>"
        country_code = "US"
        phone = a.get("phone") or "<MISSING>"
        latitude = a.get("latitude") or "<MISSING>"
        longitude = a.get("longitude") or "<MISSING>"
        hours_of_operation = (
            "".join(a.get("hours")).replace("\n", " ").replace("\r", " ").strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split()) or "<MISSING>"
        store_number = j.get("location").get("id")

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
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        max_search_distance_miles=100,
        expected_search_radius_miles=100,
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
            SgRecordID({SgRecord.Headers.STORE_NUMBER}),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        fetch_data(writer)
