from typing import Iterable, T_co, Tuple, Callable
from sgscrape.sgrecord_id import SgRecordID, RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.pause_resume import CrawlStateSingleton
from sgrequests.sgrequests import SgRequests
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch, Grain_4
from sgzip.parallel import DynamicSearchMaker, ParallelDynamicSearch, SearchIteration
import os
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("massimodutti")

DEFAULT_PROXY_URL = "https://groups-RESIDENTIAL,country-us:{}@proxy.apify.com:8000/"


def set_proxies():
    if "PROXY_PASSWORD" in os.environ and os.environ["PROXY_PASSWORD"].strip():

        proxy_password = os.environ["PROXY_PASSWORD"]
        url = (
            os.environ["PROXY_URL"] if "PROXY_URL" in os.environ else DEFAULT_PROXY_URL
        )
        proxy_url = url.format(proxy_password)
        proxies = {
            "https://": proxy_url,
        }
        return proxies
    else:
        return None


_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.massimodutti.com/"
base_url = "https://www.massimodutti.com/itxrest/2/bam/store/34009456/physical-store?appId=1&languageId=-1&latitude={}&longitude={}&favouriteStores=false&lastStores=false&closerStores=true&min=10&radioMax=100&receiveEcommerce=false&showBlockedMaxPackage=false"

days = [
    "",
    "Sunday",
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
]


class ExampleSearchIteration(SearchIteration):
    def __init__(self, http: SgRequests):
        self._http = http
        self.__state = CrawlStateSingleton.get_instance()

    def do(
        self,
        coord: Tuple[float, float],
        zipcode: str,
        current_country: str,
        items_remaining: int,
        found_location_at: Callable[[float, float], None],
    ) -> Iterable[SgRecord]:

        # here you'd use self.__http, and call `found_location_at(lat, long)` for all records you find.
        locations = self._http.get(
            base_url.format(coord[0], coord[1]), headers=_headers
        ).json()["closerStores"]
        logger.info(f"[{current_country}] found: {len(locations)}")
        for store in locations:
            hours = []
            for hr in store.get("openingHours", {}).get("schedule", []):
                times = f"{hr['timeStripList'][0]['initHour']}-{hr['timeStripList'][0]['initHour']}"
                for hh in hr["weekdays"]:
                    hours.append(f"{days[hh]}: {times}")
            phone = ""
            if store.get("phones"):
                phone = store["phones"][0]

            yield SgRecord(
                page_url=store["url"],
                store_number=store["id"],
                street_address=" ".join(store["addressLines"]),
                city=store["city"],
                state=store["state"],
                zip_postal=store["zipCode"],
                latitude=coord[0],
                longitude=coord[1],
                phone=phone,
                country_code=store["countryCode"],
                hours_of_operation="; ".join(hours),
            )
        # just some clever accounting of locations/country:
        rec_count = self.__state.get_misc_value(
            current_country, default_factory=lambda: 0
        )
        self.__state.set_misc_value(current_country, rec_count + len(locations))


if __name__ == "__main__":
    search_maker = DynamicSearchMaker(
        use_state=False, search_type="DynamicGeoSearch", granularity=Grain_4()
    )

    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        with SgRequests() as http:
            http.proxies = set_proxies()
            search_iter = ExampleSearchIteration(http=http)
            par_search = ParallelDynamicSearch(
                search_maker=search_maker,
                search_iteration=search_iter,
                country_codes=SearchableCountries.ALL,
                max_threads=1,
            )

            for rec in par_search.run():
                writer.write_row(rec)
