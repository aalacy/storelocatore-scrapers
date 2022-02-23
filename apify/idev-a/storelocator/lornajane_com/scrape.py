from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgzip.parallel import DynamicSearchMaker, ParallelDynamicSearch, SearchIteration
from typing import Iterable, Tuple, Callable
from sgrequests.sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgpostal.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("lornajane")
locator_domain = "https://www.lornajane.com"
base_url = "https://www.lornajane.co.uk/on/demandware.store/Sites-LJUK-Site/en_GB/Stores-FindStores?country={}&latitude={}&longitude={}"

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
            url = base_url.format(current_country.upper(), lat, lng)
            locations = bs(session.get(url, headers=_headers).text, "lxml").select(
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
                sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
                hours = []
                if sp1.select_one("div.store-hours"):
                    hours = list(sp1.select_one("div.store-hours").stripped_strings)
                if hours:
                    hours = hours[1:]
                yield SgRecord(
                    page_url=page_url,
                    locator_domain=locator_domain,
                    street_address=" ".join(_addr[:-1]).replace("\n", ""),
                    city=addr.city,
                    state=addr.state,
                    zip_postal=addr.postcode,
                    country_code=addr.country,
                    store_number=_["data-store-id"],
                    location_name=_["data-store-name"],
                    phone=phone,
                    latitude=_coord[0],
                    longitude=_coord[1],
                    hours_of_operation="; ".join(hours),
                    raw_address=raw_address,
                )


if __name__ == "__main__":
    search_maker = DynamicSearchMaker(search_type="DynamicGeoSearch")
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.PageUrlId, duplicate_streak_failure_factor=100
        )
    ) as writer:
        search_iter = ExampleSearchIteration()
        par_search = ParallelDynamicSearch(
            search_maker=search_maker,
            search_iteration=search_iter,
            country_codes=["us", "gb", "au", "nz", "my", "sg", "fr", "ae"],
        )

        for rec in par_search.run():
            writer.write_row(rec)
