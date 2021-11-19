from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from sgrequests.sgrequests import SgRequests
from sgzip.dynamic import SearchableCountries, Grain_8
from sgzip.parallel import DynamicSearchMaker, ParallelDynamicSearch, SearchIteration
from typing import Iterable, Tuple, Callable

logger = SgLogSetup().get_logger("carrefourksa")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.carrefourksa.com"
base_url = "{}/en/store-finder?q=&page=0&storeFormat=&latitude={}&longitude={}"

country_map = {
    "kw": "https://www.carrefourkuwait.com/mafkwt",
    "sa": "https://www.carrefourksa.com/mafsau",
    "ae": "https://www.carrefourksa.com/mafsau",
    "jo": "https://www.carrefourjordan.com/mafjor",
    "pk": "https://www.carrefour.pk/mafpak",
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

        with SgRequests() as http:

            lat = coord[0]
            lng = coord[1]
            country = country_map.get(current_country)
            url = base_url.format(country, lat, lng)
            try:
                locations = http.get(url, headers=_headers).json()["data"]
            except:
                locations = []
            logger.info(f"[{current_country}] [{lat, lng}] {len(locations)}")
            if locations:
                found_location_at(lat, lng)
            for _ in locations:
                street_address = _["line1"]
                if _["line2"]:
                    street_address += " " + _["line2"]
                hours = []
                for day, hh in _["openings"].items():
                    hours.append(f"{day}: {hh}")
                yield SgRecord(
                    location_name=f"{_['displayName']} - {_['town']}",
                    street_address=street_address,
                    city=_["town"],
                    state=_.get("state"),
                    zip_postal=_.get("postalCode"),
                    country_code=current_country,
                    phone=_["phone"],
                    latitude=_["latitude"],
                    longitude=_["longitude"],
                    location_type=_["storeFormat"],
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                )


if __name__ == "__main__":
    search_maker = DynamicSearchMaker(
        search_type="DynamicGeoSearch", granularity=Grain_8()
    )
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.LOCATION_NAME,
                }
            ),
            duplicate_streak_failure_factor=100,
        )
    ) as writer:
        search_iter = ExampleSearchIteration()
        par_search = ParallelDynamicSearch(
            search_maker=search_maker,
            search_iteration=search_iter,
            country_codes=[
                SearchableCountries.SAUDI_ARABIA,
                SearchableCountries.KUWAIT,
                SearchableCountries.UNITED_ARAB_EMIRATES,
                SearchableCountries.JORDAN,
                SearchableCountries.PAKISTAN,
            ],
        )

        for rec in par_search.run():
            writer.write_row(rec)
