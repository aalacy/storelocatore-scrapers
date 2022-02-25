from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import SearchableCountries, Grain_8
from sgzip.parallel import DynamicSearchMaker, ParallelDynamicSearch, SearchIteration
from typing import Iterable, Tuple, Callable

logger = SgLogSetup().get_logger("carrossier")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
locator_domain = "https://carrossier-procolor.com/"
base_url = "https://www.procolor.com/wp-admin/admin-ajax.php?action=store_search&lat={}&lng={}&max_results=50&search_radius=6000&filter={}&autoload=1"

country_map = {"us": "129", "ca": "128"}


class ExampleSearchIteration(SearchIteration):
    def do(
        self,
        coord: Tuple[float, float],
        zipcode: str,
        current_country: str,
        items_remaining: int,
        found_location_at: Callable[[float, float], None],
    ) -> Iterable[SgRecord]:
        lat = coord[0]
        lng = coord[1]
        with SgRequests(proxy_country="us") as session:
            _filter = country_map[current_country]
            url = base_url.format(lat, lng, _filter)
            try:
                locations = session.get(url, headers=_headers).json()
            except:
                return
            logger.info(f"[{current_country}] {len(locations)} found")
            for _ in locations:
                found_location_at(_["lat"], _["lng"])
                hours = []
                if _["hours"]:
                    for hh in bs(_["hours"], "lxml").select("tr"):
                        hours.append(": ".join(hh.stripped_strings))
                street_address = _["address"]
                if _["address2"]:
                    street_address += " " + _["address2"]
                location_name = _["store"].replace("&#8217;", "'")
                slug = (
                    location_name.replace("'", "")
                    .replace("é", "e")
                    .replace("ô", "o")
                    .replace("/", "")
                    .lower()
                )
                slug = "-".join([ss.strip() for ss in slug.split() if ss.strip()])
                page_url = f"https://www.procolor.com/en-ca/shop/{slug}/"
                logger.info(page_url)
                res = session.get(page_url, headers=_headers)
                if res.status_code == 200:
                    sp1 = bs(res.text, "lxml")
                    hours = []
                    for hh in sp1.select("div.working-hours div.row"):
                        hours.append(": ".join(hh.stripped_strings))
                yield SgRecord(
                    page_url=page_url,
                    store_number=_["id"],
                    location_name=_["store"].replace("&#8217;", "'"),
                    street_address=street_address,
                    city=_["city"].strip(),
                    state=_["state"].strip(),
                    zip_postal=_["zip"],
                    latitude=_["lat"],
                    longitude=_["lng"],
                    country_code=_["country"],
                    phone=_["phone"],
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.PageUrlId, duplicate_streak_failure_factor=1000
        )
    ) as writer:
        search_maker = DynamicSearchMaker(
            use_state=False, search_type="DynamicGeoSearch", granularity=Grain_8()
        )
        search_iter = ExampleSearchIteration()
        par_search = ParallelDynamicSearch(
            search_maker=search_maker,
            search_iteration=search_iter,
            country_codes=[SearchableCountries.CANADA, SearchableCountries.USA],
        )

        for rec in par_search.run():
            writer.write_row(rec)
