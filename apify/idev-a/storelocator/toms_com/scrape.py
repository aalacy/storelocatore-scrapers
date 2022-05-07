from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import Grain_2
from sgzip.parallel import DynamicSearchMaker, ParallelDynamicSearch, SearchIteration
from typing import Iterable, Tuple, Callable
from bs4 import BeautifulSoup as bs
import re

logger = SgLogSetup().get_logger("toms.com")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.toms.com"
base_url = "https://www.toms.com/on/demandware.store/Sites-toms-us-Site/en_US/Stores-FindStores?showMap=true&radius=50&categories=&typesStores=&lat={}&long={}"


def c_map(cc):
    map_list = {"uk": "gb"}
    return map_list[cc] if map_list.get(cc) else cc


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
        with SgRequests() as session:
            locations = session.get(base_url.format(lat, lng), headers=_headers).json()[
                "stores"
            ]
            logger.info(f"[{current_country}] [{lat, lng}] {len(locations)}")
            for _ in locations:
                found_location_at(_["latitude"], _["longitude"])
                street_address = _["address1"]
                if _["address2"]:
                    street_address += " " + _["address2"]

                phone = _.get("phone")
                if phone:
                    phone = phone.split("EXT")[0]
                location_type = "retail store"
                if "toms" in _["name"].lower() or "tom's" in _["name"].lower():
                    location_type = "tom's store"
                yield SgRecord(
                    page_url="https://www.toms.com/us/store-locator",
                    store_number=_["ID"],
                    location_name=_["name"],
                    street_address=street_address.replace("\n", "").replace("\r", " "),
                    city=_.get("city"),
                    state=_.get("stateCode"),
                    zip_postal=_.get("postalCode"),
                    country_code=_["countryCode"],
                    phone=phone,
                    location_type=location_type,
                    latitude=_["latitude"],
                    longitude=_["longitude"],
                    locator_domain=locator_domain,
                )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=1000
        )
    ) as writer:
        search_maker = DynamicSearchMaker(
            search_type="DynamicGeoSearch", granularity=Grain_2()
        )
        with SgRequests() as http:
            sp1 = bs(http.get(locator_domain, headers=_headers).text, "lxml")
            countries = bs(
                sp1.find("script", string=re.compile(r"c-country-selector__item")).text,
                "lxml",
            ).select("a.c-country-selector__link span")
            c_list = []
            for cc in countries:
                c_list.append(
                    c_map(cc.text.split("(")[1].split(")")[0].lower().strip())
                )

            logger.info(f"{len(c_list)} countries")
            par_search = ParallelDynamicSearch(
                search_maker=search_maker,
                search_iteration=lambda: ExampleSearchIteration(),
                country_codes=list(set(c_list)),
            )

            for rec in par_search.run():
                writer.write_row(rec)
