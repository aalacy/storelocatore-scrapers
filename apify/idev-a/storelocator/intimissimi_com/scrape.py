from typing import Iterable, Tuple, Callable
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests.sgrequests import SgRequests
from sgzip.dynamic import SearchableCountries
from sgzip.parallel import DynamicSearchMaker, ParallelDynamicSearch, SearchIteration
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("intimissimi")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.intimissimi.com/"
base_url = "https://www.intimissimi.com/on/demandware.store/Sites-intimissimi-ww-Site/en_WS/Stores-FindStores?radius=100&lat={}&long={}&geoloc=false"


class ExampleSearchIteration(SearchIteration):
    def __init__(self, http: SgRequests):
        self._http = http

    def do(
        self,
        coord: Tuple[float, float],
        zipcode: str,
        current_country: str,
        items_remaining: int,
        found_location_at: Callable[[float, float], None],
    ) -> Iterable[SgRecord]:

        self._http.clear_cookies()
        # here you'd use self.__http, and call `found_location_at(lat, long)` for all records you find.
        res = self._http.get(base_url.format(coord[0], coord[1]), headers=_headers)
        if res.status_code == 200:
            locations = res.json()["stores"]
            logger.info(f"[{current_country}] found: {len(locations)}")
            for store in locations:
                hours = []
                for hr in store.get("storeHours", []):
                    hours.append(f"{hr['name']}: {hr['phases']}")

                street_address = store["address1"]
                if store.get("address2"):
                    street_address += " " + store["address2"]
                page_url = f'https://www.intimissimi.com/world/stores/{store["name"].lower().replace(" ","_")}/{store["ID"]}.html'
                city = store.get("city", "")
                if city:
                    street_address = street_address.replace(city, "")
                zip_postal = store.get("postalCode", "")
                if zip_postal:
                    street_address = street_address.replace(zip_postal, "")
                yield SgRecord(
                    page_url=page_url,
                    store_number=store["ID"],
                    location_name=store["name"],
                    street_address=street_address.replace(",", "")
                    .replace("&apos;", "'")
                    .strip(),
                    city=city,
                    state=store.get("state", ""),
                    zip_postal=zip_postal,
                    latitude=store["latitude"],
                    longitude=store["longitude"],
                    phone=store.get("phone"),
                    country_code=store["countryCode"],
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                )


if __name__ == "__main__":
    search_maker = DynamicSearchMaker(
        use_state=False,
        search_type="DynamicGeoSearch",
        expected_search_radius_miles=100,
    )

    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        with SgRequests(
            proxy_country="us", proxy_rotation_failure_threshold=15
        ) as http:
            search_iter = ExampleSearchIteration(http=http)
            par_search = ParallelDynamicSearch(
                search_maker=search_maker,
                search_iteration=search_iter,
                country_codes=SearchableCountries.ALL,
            )

            for rec in par_search.run():
                writer.write_row(rec)
