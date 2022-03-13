from concurrent.futures import ThreadPoolExecutor
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch, Grain_1_KM
from sgscrape.pause_resume import CrawlStateSingleton
from sglogging import sglog

logger = sglog.SgLogSetup().get_logger(logger_name="bp.com")
max_workers = 24


def get_response(co_ord, retry=1):
    lat, lng = co_ord
    api_url = f"https://bpretaillocator.geoapp.me/api/v1/locations/nearest_to?lat={lat}&lng={lng}&autoload=true&travel_mode=driving&avoid_tolls=false&avoid_highways=false&show_stations_on_route=true&corridor_radius=5&key=AIzaSyDHlZ-hOBSpgyk53kaLADU18wq00TLWyEc&format=json"

    with SgRequests() as http:
        try:
            response = http.get(api_url, headers=headers)
            logger.info(f"HTTP STATUS Return: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                logger.info(f"From {lat,lng} stores = {len(data)}")
                return data
        except Exception as e:
            log.error(f"HTTP Error Code: {response.status_code}; retry={retry}")
            if retry == 10:
                return []
            return get_response(co_ord, retry + 1)


def fetch_data(search, sgw: SgWriter):
    with ThreadPoolExecutor(
        max_workers=max_workers, thread_name_prefix="fetcher"
    ) as executor:
        for data in executor.map(get_response, search):
            if data:
                for j in data:
                    location_name = j.get("name")
                    street_address = j.get("address")
                    city = j.get("city")
                    state = j.get("state")
                    postal = j.get("postcode") or ""
                    if "-" in postal:
                        postal = SgRecord.MISSING
                    country = j.get("country_code")
                    phone = j.get("telephone")
                    latitude = j.get("lat")
                    longitude = j.get("lng")

                    _tmp = []
                    hours = j.get("opening_hours") or []
                    for h in hours:
                        days = h.get("days") or []
                        inters = h.get("hours") or []
                        try:
                            _tmp.append(f'{"-".join(days)}: {"-".join(inters[0])}')
                        except:
                            pass

                    hours_of_operation = ";".join(_tmp)

                    row = SgRecord(
                        page_url=page_url,
                        location_name=location_name,
                        street_address=street_address,
                        city=city,
                        state=state,
                        zip_postal=postal,
                        country_code=country,
                        phone=phone,
                        latitude=latitude,
                        longitude=longitude,
                        locator_domain=locator_domain,
                        hours_of_operation=hours_of_operation,
                    )

                    sgw.write_row(row)


if __name__ == "__main__":
    CrawlStateSingleton.get_instance().save(override=True)
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:93.0) Gecko/20100101 Firefox/93.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    }
    locator_domain = "https://www.bp.com/"
    page_url = "https://www.bp.com/en_us/united-states/home/find-a-gas-station.html"
    search = DynamicGeoSearch(
        country_codes=SearchableCountries.ALL,
        granularity=Grain_1_KM(),
        expected_search_radius_miles=0.9,
        max_search_distance_miles=1,
    )
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LOCATION_NAME}
            ),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        fetch_data(search, writer)
