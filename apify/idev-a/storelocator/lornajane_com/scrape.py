from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgzip.parallel import DynamicSearchMaker, ParallelDynamicSearch, SearchIteration
from sgzip.dynamic import Grain_2
from typing import Iterable, Tuple, Callable
from sgrequests.sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgpostal.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("lornajane")
locator_domain = "https://www.lornajane.com"
base_url = "https://www.lornajane.co.uk/on/demandware.store/Sites-LJ{}-Site/en_GB/Stores-FindStores?country={}&latitude={}&longitude={}"

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

cc_map = {
    "us": "United States",
    "gb": "United Kingdom",
    "au": "Austrailia",
    "nz": "New Zealand",
    "ca": "Canada",
    "sg": "Singapore",
}

url_map = {"gb": "UK", "sg": "SG", "us": "UK", "au": "UK", "nz": "UK"}


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
        with SgRequests(proxy_country=current_country.lower()) as session:
            url = base_url.format(
                url_map[current_country], current_country.upper(), lat, lng
            )
            locations = bs(session.get(url).text, "lxml").select(
                "div.results div.store-item"
            )
            logger.info(f"[{current_country}] [{lat, lng}] {len(locations)}")
            for _ in locations:
                _addr = list(_.select_one("div.store-address").stripped_strings)
                if _addr[0].startswith("Shop"):
                    del _addr[0]
                raw_address = " ".join(_addr).replace("\n", "")
                addr = parse_address_intl(raw_address + ", " + cc_map[current_country])
                phone = ""
                if _.select_one("a.storelocator-phone"):
                    phone = _.select_one("a.storelocator-phone").text.strip()
                if phone == "null":
                    phone = ""
                try:
                    _coord = (
                        _.select_one("a.store-map")["href"].split("addr=")[1].split(",")
                    )
                    found_location_at(_coord[0], _coord[1])
                except:
                    _coord = ["", ""]
                page_url = _.select_one("div.store-name a")["href"]
                sp1 = bs(session.get(page_url).text, "lxml")
                hours = []
                if sp1.select_one("div.store-hours"):
                    hours = list(sp1.select_one("div.store-hours").stripped_strings)
                if hours:
                    hours = hours[1:]
                city = addr.city
                if not city:
                    city = _["data-store-name"].replace("Uniquely", "").strip()

                state = addr.state
                if not state and "Auckland" in raw_address:
                    state = "Auckland"
                yield SgRecord(
                    page_url=page_url,
                    store_number=_["data-store-id"],
                    location_name=_["data-store-name"],
                    locator_domain=locator_domain,
                    street_address=" ".join(_addr[:-1]).replace("\n", ""),
                    city=city,
                    state=state,
                    zip_postal=addr.postcode,
                    country_code=addr.country,
                    phone=phone,
                    latitude=_coord[0],
                    longitude=_coord[1],
                    hours_of_operation="; ".join(hours),
                    raw_address=raw_address,
                )


if __name__ == "__main__":
    search_maker = DynamicSearchMaker(
        search_type="DynamicGeoSearch", granularity=Grain_2()
    )
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.PageUrlId, duplicate_streak_failure_factor=100
        )
    ) as writer:
        search_iter = ExampleSearchIteration()
        par_search = ParallelDynamicSearch(
            search_maker=search_maker,
            search_iteration=search_iter,
            country_codes=["au", "nz", "sg"],
        )
        for rec in par_search.run():
            writer.write_row(rec)
