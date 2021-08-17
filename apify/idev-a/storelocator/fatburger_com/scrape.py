from typing import Iterable, Tuple, Callable
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.pause_resume import CrawlStateSingleton
from sgrequests.sgrequests import SgRequests
from sgzip.dynamic import SearchableCountries, Grain_4
from sgzip.parallel import DynamicSearchMaker, ParallelDynamicSearch, SearchIteration
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("fatburger")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://fatburger.com/"
base_url = "https://api.momentfeed.com/v1/analytics/api/llp.json?auth_token=BBOAPSVZOXCPKFUV&center={},{}&coordinates={},{},{},{}&multi_account=true&page=1&pageSize=1000"

hr_obj = {
    "1": "Monday",
    "2": "Tuesday",
    "3": "Wednesday",
    "4": "Thursday",
    "5": "Friday",
    "6": "Saturday",
    "7": "Sunday",
}


def _time(val):
    val = str(val)
    if len(val) == 3:
        val = "0" + val
    return val[:2] + ":" + val[2:]


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
        a1 = coord[0] - 1.42754794932
        b1 = coord[1] + 1.71661376953
        a2 = coord[0] + 1.42754794932
        b2 = coord[1] - 1.71661376953
        locations = self._http.get(
            base_url.format(coord[0], coord[1], a1, b1, a2, b2), headers=_headers
        ).json()
        for store in locations:
            if store["status"] != "open":
                continue
            _ = store["store_info"]
            street_address = _["address"]
            if _["address_extended"]:
                street_address += " " + _["address_extended"]
            hours = []
            if _.get("store_hours"):
                for hh in _["store_hours"].split(";"):
                    if not hh:
                        continue
                    hr = hh.split(",")
                    hours.append(f"{hr_obj[hr[0]]}: {_time(hr[1])}-{_time(hr[2])}")
            yield SgRecord(
                page_url=_["website"],
                location_name=_["name"],
                street_address=street_address,
                city=_["locality"],
                state=_.get("region"),
                zip_postal=_.get("postcode"),
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code=_["country"],
                phone=_["phone"],
                location_type=_["brand_name"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )
        logger.info(f"[{current_country}] {len(locations)}")
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
        with SgRequests(proxy_country="us") as http:
            http.clear_cookies()
            search_iter = ExampleSearchIteration(http=http)
            par_search = ParallelDynamicSearch(
                search_maker=search_maker,
                search_iteration=search_iter,
                country_codes=SearchableCountries.ALL,
                max_threads=8,
            )

            for rec in par_search.run():
                writer.write_row(rec)
