from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch
from sgscrape.pause_resume import CrawlStateSingleton
from sglogging import sglog
from tenacity import retry, stop_after_attempt
import tenacity

logger = sglog.SgLogSetup().get_logger(logger_name="bp.com")


@retry(stop=stop_after_attempt(10), wait=tenacity.wait_fixed(5))
def get_response(api_url):
    with SgRequests() as http:
        response = http.get(api_url, headers=headers)
        logger.info(f"HTTP STATUS Return: {response.status_code}")
        if response.status_code == 200:
            return response
        raise Exception(f"HTTP Error Code: {response.status_code}")


def fetch_data(coords, sgw: SgWriter):
    lat, lng = coords
    api = f"https://bpretaillocator.geoapp.me/api/v1/locations/nearest_to?lat={lat}&lng={lng}&with_all%5Bfacilities%5D%5B%5D=wild_bean_cafe&autoload=true&travel_mode=driving&avoid_tolls=false&avoid_highways=false&show_stations_on_route=true&corridor_radius=5&format=json"

    r = get_response(api)
    js = r.json()
    logger.info(f"From {lat,lng} stores = {len(js)}")
    if js:

        for j in js:
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
    locator_domain = "https://www.bp.com/en/global/corporate/who-we-are/our-brands/wild-bean-cafe.html"
    page_url = "https://www.bp.com/en_au/australia/home/who-we-are/find-your-nearest-bp/find-your-nearest-wild-bean-cafe.html"
    search = DynamicGeoSearch(
        country_codes=SearchableCountries.ALL,
        expected_search_radius_miles=50,
    )
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LOCATION_NAME}
            ),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        for p in search:
            fetch_data(p, writer)
