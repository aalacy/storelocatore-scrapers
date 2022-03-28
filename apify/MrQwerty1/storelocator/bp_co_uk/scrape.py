import tenacity
from typing import Iterable, Tuple, Callable

from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.pause_resume import CrawlStateSingleton
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.parallel import DynamicSearchMaker, ParallelDynamicSearch, SearchIteration
from tenacity import retry, stop_after_attempt


@retry(stop=stop_after_attempt(10), wait=tenacity.wait_fixed(5))
def get_response(api_url):
    with SgRequests() as http:
        response = http.get(api_url, headers=headers)
        logger.info(f"HTTP STATUS Return: {response.status_code}")
        if response.status_code == 200:
            return response
        raise Exception(f"HTTP Error Code: {response.status_code}")


class ExampleSearchIteration(SearchIteration):
    def do(
        self,
        coord: Tuple[float, float],
        zipcode: str,
        current_country: str,
        items_remaining: int,
        found_location_at: Callable[[float, float], None],
    ) -> Iterable[SgRecord]:

        lat, lng = coord
        api = f"https://bpretaillocator.geoapp.me/api/v1/locations/nearest_to?lat={lat}&lng={lng}&autoload=true&travel_mode=driving&avoid_tolls=false&avoid_highways=false&show_stations_on_route=true&corridor_radius=5&key=AIzaSyDHlZ-hOBSpgyk53kaLADU18wq00TLWyEc&format=json"
        r = get_response(api)
        js = r.json()
        logger.info(f"From {lat, lng} stores = {len(js)}")
        if js:
            for j in js:
                location_name = j.get("name")
                street_address = j.get("address")
                city = j.get("city")
                region = j.get("state")
                postal = j.get("postcode") or ""
                if "-" in postal:
                    postal = SgRecord.MISSING
                country = j.get("country_code")
                logger.info(f"Country code: {country}")
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

                yield SgRecord(
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=region,
                    zip_postal=postal,
                    country_code=country,
                    phone=phone,
                    latitude=latitude,
                    longitude=longitude,
                    locator_domain=locator_domain,
                    hours_of_operation=hours_of_operation,
                )


if __name__ == "__main__":
    logger = sglog.SgLogSetup().get_logger(logger_name="bp.co.uk")
    CrawlStateSingleton.get_instance().save(override=True)
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    }
    locator_domain = "https://www.bp.co.uk/"
    page_url = "https://www.bp.com/en_gb/united-kingdom/home/products-and-services/our-sites/find-your-nearest-bp.html"
    search_maker = DynamicSearchMaker(
        search_type="DynamicGeoSearch",
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
        search_iter = ExampleSearchIteration()
        par_search = ParallelDynamicSearch(
            search_maker=search_maker,
            search_iteration=search_iter,
            country_codes=[
                "AT",
                "AU",
                "CH",
                "DE",
                "ES",
                "FR",
                "GB" "GR",
                "LU",
                "NL",
                "PL",
                "RU",
                "SA",
                "TR",
                "ZA",
            ],
        )

        for rec in par_search.run():
            writer.write_row(rec)
