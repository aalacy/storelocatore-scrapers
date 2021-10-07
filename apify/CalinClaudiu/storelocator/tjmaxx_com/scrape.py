from typing import Iterable, Tuple, Callable
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.pause_resume import CrawlStateSingleton
from sgrequests.sgrequests import SgRequests
from sgzip.dynamic import SearchableCountries, Grain_8
from sgzip.parallel import DynamicSearchMaker, ParallelDynamicSearch, SearchIteration
from sglogging import sglog

logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")

def nice_locs(resp):
    
def fix_comma(x):
    h = []
    try:
        for i in x.split(","):
            if len(i.strip()) >= 1:
                h.append(i)
        return ", ".join(h)
    except Exception:
        return x


class ExampleSearchIteration(SearchIteration):
    """
    Here, you define what happens with each iteration of the search.
    The `do(...)` method is what you'd do inside of the `for location in search:` loop
    It provides you with all the data you could get from the search instance, as well as
    a method to register found locations.
    """

    def __init__(self, http: SgRequests):
        self.__http = http
        self.__state = CrawlStateSingleton.get_instance()

    def do(
        self,
        coord: Tuple[float, float],
        zipcode: str,
        current_country: str,
        items_remaining: int,
        found_location_at: Callable[[float, float], None],
    ) -> Iterable[SgRecord]:
        """
        This method gets called on each iteration of the search.
        It provides you with all the data you could get from the search instance, as well as
        a method to register found locations.

        :param coord: The current coordinate (lat, long)
        :param zipcode: The current zipcode (In DynamicGeoSearch instances, please ignore!)
        :param current_country: The current country (don't assume continuity between calls - it's meant to be parallelized)
        :param items_remaining: Items remaining in the search - per country, if `ParallelDynamicSearch` is used.
        :param found_location_at: The equivalent of `search.found_location_at(lat, long)`
        """

        # here you'd use self.__http, and call `found_location_at(lat, long)` for all records you find.
        lat, lng = coord
        # just some clever accounting of locations/country:
        numbers = "0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99"
        url = str(f"https://marketingsl.tjx.com/storelocator/GetSearchResults?geolat={lat}&geolong={lng}&chain={numbers}&maxstores=9999&radius=1000")
        headers = {}
        headers[
            "accept"
        ] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
        headers["accept-encoding"] = "gzip, deflate, br"
        headers["accept-language"] = "en-US,en;q=0.9"
        headers["cache-control"] = "no-cache"
        headers["pragma"] = "no-cache"
        headers[
            "user-agent"
        ] = "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        locations = None
        try:
            locations = SgRequests.raise_on_err(http.get(url, headers=headers)).json()
            errorName = None
        except Exception as e:
            logzilla.error(f"{e}")

        if locations:
            for rec in nice_locs(locations):
                yield rec


if __name__ == "__main__":
    # additionally to 'search_type', 'DynamicSearchMaker' has all options that all `DynamicXSearch` classes have.
    search_maker = DynamicSearchMaker(
        search_type="DynamicGeoSearch",
        granularity=Grain_8(),
        expected_search_radius_miles=None,
    )

    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumAndPageUrlId)
    ) as writer:
        with SgRequests() as http:
            search_iter = ExampleSearchIteration(http=http)
            par_search = ParallelDynamicSearch(
                search_maker=search_maker,
                search_iteration=search_iter,
                country_codes=SearchableCountries.ALL,
            )

            for rec in par_search.run():
                writer.write_row(rec)
