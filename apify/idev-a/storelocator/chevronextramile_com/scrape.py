from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from concurrent import futures
import dirtyjson as json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("ch")

locator_domain = "https://www.chevronwithtechron.com/"
locator_url = "https://www.chevronextramile.com/station-finder"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
}


def get_data(coords, search, sgw: SgWriter, token, session):
    lat, long = coords
    api_url = f"https://apis.chevron.com/api/StationFinder/nearby?radius=3500&lat={str(lat)}&lng={str(long)}&clientid={token}&search5=1"

    js = session.get(api_url, headers=headers).json()["stations"]

    if js:
        search.found_location_at(lat, long)

    logger.info(f"{lat, long} {len(js)}")
    for j in js:
        store_number = j.get("id")
        location_name = j.get("name") or "<MISSING>"
        street_address = j.get("address") or "<MISSING>"
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        country_code = "US"
        page_url = f"https://www.chevronextramile.com/station-finder/{street_address.replace(' ','-').lower()}-{city.replace(' ','-').lower()}-{state.lower()}-{postal}-id{store_number}/"
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        hours_of_operation = j.get("hours") or "<MISSING>"

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
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
    )
    with SgRequests(verify_ssl=False, proxy_country="us") as session:
        token = json.loads(
            session.get(locator_url, headers=headers)
            .text.split("var siteData =")[1]
            .split(";")[0]
            .strip()
        )["storeFinderAPIKey"]

        with futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_url = {
                executor.submit(get_data, url, coords, sgw, token, session): url
                for url in coords
            }
            for future in futures.as_completed(future_to_url):
                future.result()


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
