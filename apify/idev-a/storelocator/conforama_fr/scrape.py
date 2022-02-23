from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgrequests.sgrequests import SgRequests
from sgzip.dynamic import SearchableCountries, Grain_4
from sgzip.parallel import DynamicSearchMaker, ParallelDynamicSearch, SearchIteration
import dirtyjson as json
from bs4 import BeautifulSoup as bs
from typing import Iterable, Tuple, Callable
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("")

_headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.conforama.fr"
base_url = "https://www.conforama.fr/liste-des-magasins/resultat?lat={}&long={}&query="


class ExampleSearchIteration(SearchIteration):
    def do(
        self,
        coord: Tuple[float, float],
        zipcode: str,
        current_country: str,
        items_remaining: int,
        found_location_at: Callable[[float, float], None],
    ) -> Iterable[SgRecord]:

        with SgRequests(proxy_country="us") as http:
            lat = coord[0]
            lng = coord[1]
            res = http.get(base_url.format(lat, lng), headers=_headers)
            try:
                locations = json.loads(
                    res.text.split("populateListeMagasins(")[-1].split(");")[0].strip()
                )
            except:
                locations = []

            logger.info(f"[{current_country}] [{lat, lng}] {len(locations)}")
            for _ in locations:
                for x, aa in enumerate(_["address"]):
                    if not aa:
                        _["address"][x] = ""
                found_location_at(_["coords"][0], _["coords"][1])
                page_url = locator_domain + _["linkMag"]["toMag"]
                logger.info(page_url)
                sp1 = bs(http.get(page_url, headers=_headers))
                hours = []
                for hh in sp1.select("ul.list-horaires li"):
                    if not hh.text.strip():
                        continue
                    ss = list(hh.stripped_strings)
                    hours.append(f"{ss[0]}: {' '.join(ss[1:])}")

                phone = ""
                if sp1.select_one("div#telSurTaxeOrder"):
                    phone = sp1.select_one("div#telSurTaxeOrder").text.strip()
                yield SgRecord(
                    page_url=page_url,
                    location_name=_["title"],
                    store_number=_["storeId"],
                    street_address=" ".join(_["address"][:-1]),
                    city=" ".join(_["address"][2].split(",")[0].strip().split()[1:]),
                    zip_postal=_["address"][2].split(",")[0].strip().split()[0],
                    country_code=_["address"][2].split(",")[-1],
                    latitude=_["coords"][0],
                    longitude=_["coords"][1],
                    phone=phone,
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours)
                    .replace("\r", "")
                    .replace("\n", ""),
                    raw_address=" ".join(_["address"]),
                )


if __name__ == "__main__":
    search_maker = DynamicSearchMaker(
        search_type="DynamicGeoSearch", granularity=Grain_4()
    )

    search_iter = ExampleSearchIteration()
    par_search = ParallelDynamicSearch(
        search_maker=search_maker,
        search_iteration=search_iter,
        country_codes=[SearchableCountries.FRANCE],
    )
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=100
        )
    ) as writer:
        for rec in par_search.run():
            writer.write_row(rec)
